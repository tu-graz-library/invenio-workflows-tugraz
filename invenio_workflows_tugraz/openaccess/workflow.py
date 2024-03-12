# -*- coding: utf-8 -*-
#
# Copyright (C) 2022-2025 Graz University of Technology.
#
# invenio-workflows-tugraz is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Open Access Workflow."""


from flask_principal import Identity
from invenio_pure import PureRuntimeError
from invenio_pure.records.models import PureRESTError
from invenio_pure.services import PureRESTService
from invenio_pure.types import PureID
from invenio_records_marc21 import (
    DuplicateRecordError,
    Marc21Metadata,
    check_about_duplicate,
    create_record,
    current_records_marc21,
)
from invenio_records_resources.services.records.results import RecordItem
from marshmallow.exceptions import ValidationError
from sqlalchemy.orm.exc import StaleDataError

from .convert import Pure2Marc21
from .types import PureId
from .utils import change_to_exported, extract_files


def openaccess_filter() -> dict:
    """Openaccess filter."""
    return {
        "keywordUris": ["dk/atira/pure/researchoutput/keywords/export2repo/validated"],
    }


def import_func(
    identity: Identity,
    pure_id: PureID,
    pure_service: PureRESTService,
) -> RecordItem:
    """Import record from pure into the repository."""
    marc21_service = current_records_marc21.records_service

    try:
        check_about_duplicate(PureId(pure_id))
    except DuplicateRecordError as error:
        raise RuntimeError(str(error)) from error

    try:
        pure_record = pure_service.get_metadata(identity, pure_id)
        files = extract_files(pure_record)
        file_paths = [pure_service.download_file(identity, file_) for file_ in files]
    except (PureRESTError, PureRuntimeError) as error:
        raise RuntimeError(str(error)) from error

    marc21_record = Marc21Metadata()
    converter = Pure2Marc21()
    converter.convert(pure_record, marc21_record)

    data = marc21_record.json
    data["access"] = {
        "record": "public",
        "files": "public",
    }

    try:
        record = create_record(
            marc21_service,
            data,
            file_paths,
            identity,
            do_publish=False,
        )
        # validate the draft here so that the record could be marked as exported
        # because the publish will go through without problems
        marc21_service.validate_draft(
            identity,
            id_=record.id,
            ignore_field_permissions=True,
        )
    except StaleDataError as error:
        msg = f"ERROR: PureImport StaleDataError pure_id: {pure_id}"
        raise RuntimeError(msg) from error
    except ValidationError as error:
        msg = f"ERROR: PureImport ValidationError pure_id: {pure_id}, error: {error}"
        raise RuntimeError(msg) from error

    try:
        change_to_exported(pure_record)
        pure_service.mark_as_exported(identity, pure_id, pure_record)
    except PureRESTError as error:
        raise RuntimeError(str(error)) from error

    # since the valid import has been checked directly after creating the draft
    # the publish should work without errors.
    marc21_service.publish(id_=record.id, identity=identity)

    return record
