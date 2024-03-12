# -*- coding: utf-8 -*-
#
# Copyright (C) 2022-2024 Graz University of Technology.
#
# invenio-workflows-tugraz is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Theses Workflows."""


from pathlib import Path
from typing import NamedTuple, Union

from flask_principal import Identity
from invenio_access.permissions import system_identity
from invenio_alma import AlmaRESTService, AlmaSRUService
from invenio_alma.services import AlmaAPIError, AlmaRESTError
from invenio_alma.utils import is_duplicate_in_alma, validate_date
from invenio_campusonline import CampusOnlineRESTService
from invenio_campusonline.records.models import CampusOnlineRESTError
from invenio_campusonline.types import CampusOnlineID, ThesesFilter
from invenio_campusonline.utils import extract_embargo_range
from invenio_pidstore.errors import PIDDoesNotExistError
from invenio_records_marc21 import (
    DuplicateRecordError,
    Marc21Metadata,
    MarcDraftProvider,
    check_about_duplicate,
    convert_json_to_marc21xml,
    create_record,
    current_records_marc21,
)
from invenio_records_marc21.services.record.types import ACNumber
from invenio_records_resources.services.records.results import RecordItem
from marshmallow.exceptions import ValidationError
from sqlalchemy.orm.exc import NoResultFound, StaleDataError

from ..proxies import current_workflows_tugraz
from .convert import CampusOnlineToMarc21
from .types import CampusOnlineId

error_record = NamedTuple("ErrorRecord", ["id"])


@check_about_duplicate.register
def _(value: CampusOnlineId) -> None:
    """Check about double campus online id."""
    check_about_duplicate(str(value), value.category)


def theses_filter() -> ThesesFilter:
    """Return a ThesesFilter object for open records.

    FILTER: xml filter to get open records
    return ThesesFilter
    """
    start_time_tag = "<bas:from>2022-11-17T00:01:00+00:00</bas:from>"
    filter_ = f"""
        <bas:thesesType>ALL</bas:thesesType>
        <bas:state name="IFG" negate="false">{start_time_tag}</bas:state>
        <bas:state name="PUBLISHABLE" negate="false"></bas:state>
        <bas:state name="ARCH" negate="true"></bas:state>
        <bas:state name="PUB" negate="true"></bas:state>
    """

    return ThesesFilter(filter_)


def theses_create_aggregator() -> list[tuple[str, str]]:
    """Return list of marc21,cmsid tuple which should be created in alma."""
    theses_service = current_workflows_tugraz.theses_service
    return theses_service.get_ready_to(system_identity, state="create_in_alma")


def theses_update_aggregator() -> list[tuple[str, str]]:
    """Return a list of tuple(marc21, cms_id) which should be updated in repo."""
    theses_service = current_workflows_tugraz.theses_service
    return theses_service.get_ready_to(system_identity, state="update_in_repo")


def import_from_alma_func(
    identity: Identity,
    ac_number: str,
    file_path: str,
    access: str,
    embargo: Union[str, None] = None,  # change: str|None after end python3.9 support
    marcid: Union[str, None] = None,
    alma_service: AlmaSRUService = None,
    **_: dict,
) -> None:
    """Process a single import by cli of a alma record by ac number.

    Embargo has to be YYYY-MM-DD
    """
    if not alma_service:
        msg = "ERROR: alma_service for import_from_alma_func not set."
        raise RuntimeError(msg)
    marc21_service = current_records_marc21.records_service

    if marcid:
        MarcDraftProvider.predefined_pid_value = marcid

    if embargo and not validate_date(embargo):
        msg = (f"NotValidEmbargo search_value: {ac_number}, embargo: {embargo}",)
        raise RuntimeError(msg)

    try:
        check_about_duplicate(ACNumber(ac_number))
    except DuplicateRecordError as error:
        raise RuntimeError(str(error)) from error

    try:
        metadata = alma_service.get_record(ac_number)[0]
    except AlmaRESTError as error:
        msg = f"ERROR: alma rest search_value: {ac_number}, error: {error}"
        raise RuntimeError(msg) from error

    marc21_record = Marc21Metadata(metadata=metadata)

    data = marc21_record.json
    data["access"] = {
        "record": "public",
        "files": "public" if access == "public" else "restricted",
    }

    if not Path(file_path).is_file():
        msg = f"ERROR: FileNotFoundError search_value: {ac_number}, file_path: {file_path}"  # noqa: E501
        raise RuntimeError(msg)

    if embargo:
        data["access"]["embargo"] = {
            "until": embargo,
            "active": True,
            "reason": None,
        }

    try:
        record = create_record(marc21_service, data, [file_path], identity)
    except StaleDataError as error:
        msg = f"ERROR: StaleDataError search_value: {ac_number}"
        raise RuntimeError(msg) from error
    except ValidationError as error:
        msg = f"ValidationError   search_value: {ac_number}, error: {error}"
        raise RuntimeError(msg) from error

    return record


def import_from_cms_func(
    identity: Identity,
    cms_id: CampusOnlineID,
    cms_service: CampusOnlineRESTService,
) -> RecordItem:
    """Import the record into the repository from campusonline."""
    marc21_service = current_records_marc21.records_service
    theses_service = current_workflows_tugraz.theses_service

    try:
        check_about_duplicate(CampusOnlineId(cms_id))
    except DuplicateRecordError as error:
        raise RuntimeError(str(error)) from error

    try:
        thesis = cms_service.get_metadata(identity, cms_id)
        file_path = cms_service.download_file(identity, cms_id)
    except CampusOnlineRESTError as error:
        raise RuntimeError(str(error)) from error

    marc21_record = Marc21Metadata()
    converter = CampusOnlineToMarc21(marc21_record)
    converter.convert(thesis, marc21_record)

    data = marc21_record.json
    data["access"] = {
        "record": "restricted",
        "files": "restricted",
    }

    if bool(_ := extract_embargo_range(thesis)):
        # the embargo end date from tugonline is ignored on purpose and set to a
        # infinity value to express that the enddate will not be reached!
        # the requirement forces a manual removal of the embargo.
        data["access"]["embargo"] = {
            "until": "9999-12-12",
            "active": True,
            "reason": None,
        }

    try:
        record = create_record(
            marc21_service,
            data,
            [file_path],
            identity,
            do_publish=False,
        )
    except StaleDataError as error:
        msg = f"ERROR: StaleDataError cms_id: {cms_id}"
        raise RuntimeError(msg) from error
    except ValidationError as error:
        msg = f"ValidationError cms_id: {cms_id}, error: {error}"
        raise RuntimeError(msg) from error

    theses_service.create(identity, record.id, cms_id)
    theses_service.set_state(identity, id_=record.id, state="imported_in_repo")

    return record


def create_func(
    identity: Identity,
    marc_id: str,
    cms_id: str,
    alma_service: AlmaRESTService,
) -> None:
    """Create a record in alma.

    Normally - depending on the API_KEY - the record will be created in
    the Institution Zone (IZ).
    """
    marc21_service = current_records_marc21.records_service
    theses_service = current_workflows_tugraz.theses_service

    if is_duplicate_in_alma(cms_id):
        msg = f"WARNING: duplicate in alma cms_id: {cms_id}"
        raise RuntimeWarning(msg)

    try:
        record = marc21_service.read_draft(identity, marc_id)
    except (NoResultFound, PIDDoesNotExistError) as error:
        msg = f"ERROR: marc_id: {marc_id}, cms_id: {cms_id} not found in db"
        raise RuntimeError(msg) from error

    marc21_record_etree = convert_json_to_marc21xml(record.to_dict()["metadata"])

    try:
        alma_service.create_record(marc21_record_etree)
    except AlmaRESTError as error:
        msg = f"ERROR: alma rest error on marc_id: {marc_id}, cms_id: {cms_id}, error: {error}"  # noqa: E501
        raise RuntimeError(msg) from error

    theses_service.set_state(identity, id_=marc_id, state="created_in_alma")


def update_func(
    identity: Identity,
    marc_id: str,
    cms_id: str,
    alma_service: AlmaSRUService,
    *,
    update_access: bool = True,
) -> None:
    """Update the record by metadata from alma.

    :param bool update_access: normally true, but if updated by cli it would be
    nice to update records without worring to mess up the access.
    """
    marc21_service = current_records_marc21.records_service
    theses_service = current_workflows_tugraz.theses_service

    try:
        data = marc21_service.read_draft(id_=marc_id, identity=identity).data
    except (NoResultFound, PIDDoesNotExistError):
        try:
            # if this raises also the NoResultFound error it should break!
            data = marc21_service.read(id_=marc_id, identity=identity).data
        except (NoResultFound, PIDDoesNotExistError) as error:
            msg = f"ERROR: update record marc_id: {marc_id}, cms_id: {cms_id} not found in db"  # noqa: E501
            raise RuntimeError(msg) from error

    if update_access:
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
        data["access"]["record"] = "public"
        data["access"]["files"] = "restricted" if is_restricted else "public"

    try:
        alma_marc21_etree = alma_service.get_record(cms_id, "local_field_995")
    except (AlmaRESTError, AlmaAPIError) as error:
        msg = f"ERROR: alma rest marc_id: {marc_id}, cms_id: {cms_id}, error: {error}"
        raise RuntimeError(msg) from error

    alma_marc21_record = Marc21Metadata(metadata=alma_marc21_etree[0])

    # only update and publish records which are associated with
    # "verbund" and have therefore an AC* number. this also shows that
    # the record was viewed by a librarian
    ac_field = alma_marc21_record.get_value("009")
    if not ac_field.startswith("AC"):
        msg = f"marcid: {marc_id}, cms_id: {cms_id} not yet updated in alma"
        raise RuntimeError(msg)

    data["metadata"] = alma_marc21_record.json["metadata"]

    try:
        marc21_service.edit(id_=marc_id, identity=identity)
        marc21_service.update_draft(id_=marc_id, identity=identity, data=data)
        marc21_service.publish(id_=marc_id, identity=identity)
    except ValidationError as error:
        msg = f"ValidationError cms_id: {cms_id}, error: {error}"
        raise RuntimeError(msg) from error

    theses_service.set_state(identity, id_=marc_id, state="updated_in_repo")


def duplicate_func(cms_id: str) -> bool:
    """Check if the cms_id has already been imported."""
    try:
        check_about_duplicate(CampusOnlineId(cms_id))
        return False
    except DuplicateRecordError:
        return True
