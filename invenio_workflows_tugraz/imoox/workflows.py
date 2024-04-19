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
from invenio_records_lom.utils import LOMMetadata

from .visiter import MoocToLOM


def imoox_import_func(imoox_record: dict, identity: Identity) -> None:
    """Create and publish function."""
    visiter = MoocToLOM()
    lom_record = LOMMetadata()

    visiter.visit(imoox_record, lom_record)

    data = {
        "access": {"record": "public", "files": "public"},
        "files": {"enabled": False},
        "metadata": lom_record.json,
        "resource_type": "link",
    }
    lom_service = current_records_lom.records_service
    draft = lom_service.create(data=data, identity=identity)

    # to prevent the race condition bug.
    # see https://github.com/inveniosoftware/invenio-rdm-records/issues/809
    time.sleep(0.5)

    lom_service.publish(id_=draft.id, identity=identity)
