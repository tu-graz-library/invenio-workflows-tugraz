# -*- coding: utf-8 -*-
#
# Copyright (C) 2022-2025 Graz University of Technology.
#
# invenio-workflows-tugraz is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Open Access Workflow."""


from flask_principal import Identity
from invenio_access.permissions import system_identity
from invenio_pidstore.errors import PIDDoesNotExistError
from invenio_pidstore.models import PersistentIdentifier
from invenio_pure import PureRuntimeError
from invenio_pure.records.models import PureRESTError
from invenio_pure.services import PureRESTService
from invenio_pure.types import PureID
from invenio_records_marc21 import (
    Marc21Metadata,
    add_file_to_record,
    create_record,
    current_records_marc21,
)
from invenio_records_marc21.records import Marc21Draft, Marc21Record
from invenio_records_resources.services.records.results import RecordItem
from marshmallow.exceptions import ValidationError
from sqlalchemy.exc import IntegrityError, NoResultFound
from sqlalchemy.orm.exc import StaleDataError

from ..proxies import current_workflows_tugraz
from .convert import Pure2Marc21
from .utils import change_to_exported, extract_files


def openaccess_filter() -> dict:
    """Openaccess filter."""
    return {
        "keywordUris": ["dk/atira/pure/researchoutput/keywords/export2repo/validated"],
    }


def openaccess_mark_as_exported_aggregator() -> list[tuple[str, str]]:
    """Return a list of tuple[marc21, pure_id] which should be marked as exported in pure."""
    oa_service = current_workflows_tugraz.openaccess_service
    return oa_service.get_ready_to(system_identity, state="imported_in_repo")


def openaccess_import_func(  # noqa: PLR0915
    identity: Identity,
    pure_id: PureID,
    pure_service: PureRESTService,
) -> RecordItem:
    """Import record from pure into the repository."""
    marc21_service = current_records_marc21.records_service
    oa_service = current_workflows_tugraz.openaccess_service
    ignore_files = False

    try:
        # resolve record over pure_id
        pid = PersistentIdentifier.get("pure", pure_id)
        obj = pid.get_assigned_object(object_type="rec")

        try:
            draft_model = Marc21Draft.get_record(obj)
            # the edit is not necessary, but to get a resultitem draft this is the easiest way
            draft = marc21_service.edit(identity=identity, id_=draft_model["id"])
        except NoResultFound:
            record_model = Marc21Record.get_record(obj)
            draft = marc21_service.edit(identity=identity, id_=record_model["id"])
        ignore_files = True
    except PIDDoesNotExistError:
        # not found create a record
        data = {
            "files": {"enabled": True},
            "access": {
                "record": "public",
                "files": "public",
            },
        }
        draft = create_record(
            marc21_service,
            data=data,
            file_paths=[],
            identity=identity,
            do_publish=False,
        )

    try:
        pure_record = pure_service.get_metadata(identity, pure_id)
        files = extract_files(pure_record)
        file_paths = [pure_service.download_file(identity, file_) for file_ in files]
    except (PureRESTError, PureRuntimeError) as error:
        # todo: delete draft
        draft.delete_draft(identity=identity, id_=draft.id)
        raise RuntimeError(str(error)) from error

    marc21_record = Marc21Metadata()
    converter = Pure2Marc21()

    try:
        converter.convert(pure_record, marc21_record)
    except KeyError as error:
        raise RuntimeError(str(error)) from error

    # the publisher is not included in the record information
    publisher = pure_service.get_publisher_name(identity, pure_id)
    marc21_record.emplace_datafield("264..1.b", value=publisher)

    # TODO merge with draft.data
    # find out how to get data from draft
    data = draft.to_dict() | marc21_record.json
    data["pids"]["pure"] = {"provider": "pure", "identifier": pure_id}

    try:
        marc21_service.update_draft(identity, id_=draft.id, data=data)

        # TODO:
        # there exists a problem with reupload files, this is the easiest solution for the moment
        if not ignore_files:
            for file_path in file_paths:
                add_file_to_record(
                    marcid=draft.id,
                    file_path=file_path,
                    file_service=marc21_service.draft_files,
                    identity=identity,
                )

        # validate the draft here so that the record could be marked as exported
        # because the publish will go through without problems
        marc21_service.validate_draft(
            identity,
            id_=draft.id,
            ignore_field_permissions=True,
        )
    except StaleDataError as error:
        msg = f"ERROR: PureImport StaleDataError pure_id: {pure_id}"
        raise RuntimeError(msg) from error
    except ValidationError as error:
        msg = f"ERROR: PureImport ValidationError pure_id: {pure_id}, error: {error}"
        raise RuntimeError(msg) from error

    # since the valid import has been checked directly after creating the draft
    # the publish should work without errors.
    record = marc21_service.publish(id_=draft.id, identity=identity)

    try:
        oa_service.create(identity, record.id, pure_id)
    except IntegrityError:
        # if a record will be reimported after resetting the
        # ready-to-export tag in pure. the record in pure has to be
        # updated again, to make that happen the marked_as_exported
        # has to be resetted
        oa_service.set_state(
            identity,
            id_=record.id,
            state="marked_as_exported",
            value=False,
        )

    oa_service.set_state(identity, id_=record.id, state="imported_in_repo")

    return record


def openaccess_update_status_in_pure(
    identity: Identity,
    marc_id: str,
    pure_id: PureID,
    pure_service: PureRESTService,
) -> None:
    """Update status in pure."""
    oa_service = current_workflows_tugraz.openaccess_service

    try:
        # yes i know this is not nice to nicest way to get the xml record, but
        # the easiest
        pure_record = pure_service.get_metadata(identity, pure_id)
    except (PureRESTError, PureRuntimeError) as error:
        raise RuntimeError(str(error)) from error

    try:
        change_to_exported(pure_record)
        pure_service.mark_as_exported(identity, pure_id, pure_record)
    except PureRESTError as error:
        raise RuntimeError(str(error)) from error

    oa_service.set_state(identity, id_=marc_id, state="marked_as_exported")
