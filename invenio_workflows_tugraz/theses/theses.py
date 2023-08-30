# -*- coding: utf-8 -*-
#
# Copyright (C) 2022-2023 Graz University of Technology.
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
from invenio_campusonline.types import (
    CampusOnlineConfigs,
    CampusOnlineID,
    ThesesFilter,
    ThesesState,
)
from invenio_campusonline.utils import get_embargo_range
from invenio_config_tugraz import get_identity_from_user_by_email
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


def theses_filter_for_open_records() -> ThesesFilter:
    """Return a ThesesFilter object for open records.

    FILTER: xml filter to get open records
    STATE: [open, locked]
    return ThesesFilter
    """
    filter_ = [
        """<bas:thesesType>ALL</bas:thesesType>""",
        """<bas:state name="IFG" negate="false"><bas:from>2022-11-17T00:01:00+00:00</bas:from></bas:state>""",  # noqa: E501
    ]
    state = ThesesState.OPEN
    return ThesesFilter(filter_, state)


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

    if bool(embargo := get_embargo_range(thesis)):
        data["access"]["embargo"] = {
            "until": embargo.end_date,
            "active": True,
            "reason": None,
        }

    return create_record(service, data, [file_path], identity, do_publish=False)


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
    except NoResultFound:
        data = records_service.read(id_=marc_id, identity=identity).data

    marc21_etree = alma_service.get_record(cms_id, search_key="local_field_995")
    marc21_record = Marc21Metadata(metadata=marc21_etree[0])

    is_restricted = marc21_record.exists_field(
        category="971",
        ind1="7",
        ind2=" ",
        subf_code="a",
        subf_value="gesperrt",
    )
    file_access = "restricted" if is_restricted else "public"
    data["metadata"] = marc21_record.json["metadata"]
    data["access"]["record"] = "public"
    data["access"]["files"] = file_access

    records_service.edit(id_=marc_id, identity=identity)
    records_service.update_draft(id_=marc_id, identity=identity, data=data)
    records_service.publish(id_=marc_id, identity=identity)
