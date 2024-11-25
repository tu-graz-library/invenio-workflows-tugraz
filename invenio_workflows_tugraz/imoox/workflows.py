# -*- coding: utf-8 -*-
#
# Copyright (C) 2024 Graz University of Technology.
#
# invenio-workflows-tugraz is free software; you can redistribute it
# and/or modify it under the terms of the MIT License; see LICENSE
# file for more details.

"""Converter Module to facilitate conversion of metadata."""

import time

from flask_principal import Identity
from invenio_records_lom import current_records_lom
from invenio_records_lom.utils import (
    LOMDuplicateRecordError,
    LOMMetadata,
    check_about_duplicate,
)
from marshmallow.exceptions import ValidationError

from .visitor import IMOOXToLOM


def imoox_import_func(imoox_record: dict, identity: Identity, *, dry_run: bool) -> None:
    """Create and publish function."""
    course_code = imoox_record["attributes"]["courseCode"]
    try:
        check_about_duplicate(course_code, "imoox")
    except LOMDuplicateRecordError as error:
        msg = f"DRY_RUN {error}" if dry_run else str(error)
        raise RuntimeError(msg) from error

    if dry_run:
        msg = f"DRY_RUN imoox import success course_code: {course_code}"
        raise RuntimeError(msg)

    converter = IMOOXToLOM()
    lom_record = LOMMetadata()

    converter.convert(imoox_record, lom_record)

    data = {
        "access": {"record": "public", "files": "public"},
        "files": {"enabled": False},
        "metadata": lom_record.json,
        "resource_type": "link",
    }

    lom_service = current_records_lom.records_service
    try:
        draft = lom_service.create(data=data, identity=identity)

        # to prevent the race condition bug.
        # see https://github.com/inveniosoftware/invenio-rdm-records/issues/809
        time.sleep(0.5)

        return lom_service.publish(id_=draft.id, identity=identity)
    except ValidationError as error:
        msg = f"ValidationError courseCode: {course_code}, error: {error}"
        raise RuntimeError(msg) from error
