# -*- coding: utf-8 -*-
#
# Copyright (C) 2022-2024 Graz University of Technology.
#
# invenio-workflows-tugraz is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Theses Workflows."""

from collections.abc import Callable
from typing import NamedTuple
from xml.etree.ElementTree import Element

from flask_principal import Identity
from invenio_access.permissions import system_process
from invenio_alma import AlmaSRUService
from invenio_campusonline.types import CampusOnlineConfigs, CampusOnlineID, ThesesFilter
from invenio_campusonline.utils import get_embargo_range
from invenio_config_tugraz import get_identity_from_user_by_email
from invenio_pidstore.errors import PIDDoesNotExistError
from invenio_records_marc21 import (
    DuplicateRecordError,
    Marc21Metadata,
    Marc21RecordService,
    check_about_duplicate,
    create_record,
    current_records_marc21,
)
from invenio_records_resources.services.records.results import RecordItem
from invenio_search import RecordsSearch
from invenio_search.engine import dsl
from sqlalchemy.orm.exc import NoResultFound

from ..proxies import current_workflows_tugraz
from .convert import CampusOnlineToMarc21
from .types import CampusOnlineId

error_record = NamedTuple("ErrorRecord", ["id"])


@check_about_duplicate.register
def _(value: CampusOnlineId) -> None:
    """Check about double campus online id."""
    check_about_duplicate(str(value), value.category)


def cms_id(record: dict) -> str:
    """CMS id."""
    return record["_source"]["metadata"]["fields"]["995"][0]["subfields"]["a"][0]


def marc_id(record: dict) -> str:
    """Marc id."""
    return record["_source"]["id"]


def theses_filter() -> ThesesFilter:
    """Return a ThesesFilter object for open records.

    FILTER: xml filter to get open records
    return ThesesFilter
    """
    start_time_tag = "<bas:from>2022-11-17T00:01:00+00:00</bas:from>"
    _filter = f"""
        <bas:thesesType>ALL</bas:thesesType>
        <bas:state name="IFG" negate="false">{start_time_tag}</bas:state>
        <bas:state name="PUBLISHABLE" negate="false"></bas:state>
        <bas:state name="ARCH" negate="true"></bas:state>
        <bas:state name="PUB" negate="true"></bas:state>
    """

    return ThesesFilter(_filter)


def theses_create_aggregator() -> list[tuple[str, str]]:
    """Return list of marc21,cmsid tuple which should be created in alma."""
    search = RecordsSearch(index="marc21records-drafts")
    query = {
        "must_not": [
            {
                "exists": {
                    "field": "metadata.fields.001",
                },
            },
        ],
        "must": [
            {
                "exists": {
                    "field": "metadata.fields.995",
                },
            },
        ],
    }

    search.query = dsl.Q("bool", **query)
    search = search.params(size=100)
    result = search.execute()
    hits = result["hits"]["hits"]
    return [(marc_id(record), cms_id(record)) for record in hits]


def theses_update_aggregator() -> list[tuple[str, str]]:
    """Return a list of tuple(marc21, cms_id) which should be updated in repo."""
    search = RecordsSearch(index="marc21records-drafts")
    query = {
        "must_not": [
            {
                "exists": {
                    "field": "metadata.fields.001",
                },
            },
        ],
    }
    search.query = dsl.Q("bool", **query)
    result = search.execute()
    hits = result["hits"]["hits"]
    return [(marc_id(record), cms_id(record)) for record in hits]


def exists_fulltext(thesis: Element) -> bool:
    """Check against fulltext existens."""
    ns = "http://www.campusonline.at/thesisservice/basetypes"
    xpath = f".//{{{ns}}}attr[@key='VOLLTEXT']"
    ele = thesis.find(xpath)

    if ele is None:  # noqa: SIM114
        return False
    elif ele.text == "N":  # noqa: SIM103, RET505
        return False
    else:
        return True


def import_func(
    cms_id: CampusOnlineID,
    configs: CampusOnlineConfigs,
    get_metadata: Callable,
    download_file: Callable,
) -> RecordItem:
    """Import the record into the repository."""
    try:
        check_about_duplicate(CampusOnlineId(cms_id))
    except DuplicateRecordError as error:
        return str(error)

    thesis = get_metadata(configs.endpoint, configs.token, cms_id)

    if not exists_fulltext(thesis):
        msg = "record has no associated file"
        raise RuntimeError(msg)

    file_path = download_file(configs.endpoint, configs.token, cms_id)

    marc21_record = Marc21Metadata()
    convert = CampusOnlineToMarc21(marc21_record)

    convert.convert(thesis, marc21_record)

    identity = get_identity_from_user_by_email(email=configs.user_email)
    identity.provides.add(system_process)
    service = current_records_marc21.records_service
    data = marc21_record.json
    data["access"] = {
        "record": "restricted",
        "files": "restricted",
    }

    if bool(_ := get_embargo_range(thesis)):
        # the embargo end date from tugonline is ignored on purpose and set to a
        # infinity value to express that the enddate will not be reached!
        # the requirement forces a manual removal of the embargo.
        data["access"]["embargo"] = {
            "until": "9999-12-12",
            "active": True,
            "reason": None,
        }

    theses_service = current_workflows_tugraz.theses_service

    record = create_record(service, data, [file_path], identity, do_publish=False)
    theses_service.create(record.id, cms_id)

    return record


def update_func(
    records_service: Marc21RecordService,
    alma_service: AlmaSRUService,
    marc_id: str,
    cms_id: str,
    identity: Identity,
) -> None:
    """Update the record by metadata from alma."""
    try:
        data = records_service.read_draft(id_=marc_id, identity=identity).data
    except (NoResultFound, PIDDoesNotExistError):
        # if this raises also the NoResultFound error it should break!
        data = records_service.read(id_=marc_id, identity=identity).data

    db_marc21_record = Marc21Metadata(json=data["metadata"])

    # The existens of the "gesperrt" field will be checked from the
    # database metadata because the field could be removed by
    # accident. It would be a feature to open the files within the
    # repository by the metadata comming from alma but the risk of
    # exposing files without intention is to high.
    is_restricted = db_marc21_record.exists_field(
        category="971",
        ind1="7",
        ind2=" ",
        subf_code="a",
        subf_value="gesperrt",
    )

    alma_marc21_etree = alma_service.get_record(cms_id, search_key="local_field_995")
    alma_marc21_record = Marc21Metadata(metadata=alma_marc21_etree[0])

    # only update and publish records which are associated with
    # "verbund" and have therefore an AC* number. this also shows that
    # the record was viewed by a librarian
    ac_field = alma_marc21_record.get_value("009")
    if not ac_field.startswith("AC"):
        msg = f"marcid: {marc_id}, cms_id: {cms_id} not yet updated in alma"
        raise RuntimeError(msg)

    data["metadata"] = alma_marc21_record.json["metadata"]
    data["access"]["record"] = "public"
    data["access"]["files"] = "restricted" if is_restricted else "public"

    records_service.edit(id_=marc_id, identity=identity)
    records_service.update_draft(id_=marc_id, identity=identity, data=data)
    records_service.publish(id_=marc_id, identity=identity)

    theses_service = current_workflows_tugraz.theses_service
    theses_service.set_ready_to(identity, id_=marc_id, state="publish")


def duplicate_func(cms_id: str) -> bool:
    """Check if the cms_id has already been imported."""
    try:
        check_about_duplicate(CampusOnlineId(cms_id))
        return False
    except DuplicateRecordError:
        return True
