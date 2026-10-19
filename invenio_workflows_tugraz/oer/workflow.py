# -*- coding: utf-8 -*-
#
# Copyright (C) 2025 Graz University of Technology.
#
# invenio-workflows-tugraz is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""OER to Alma workflow."""

from flask_principal import Identity
from invenio_alma import AlmaRESTService
from invenio_alma.services import AlmaRESTError
from invenio_alma.utils import is_duplicate_in_alma
from invenio_pidstore.errors import PIDDoesNotExistError
from invenio_records_lom import current_records_lom
from invenio_records_marc21 import Marc21Metadata, convert_json_to_marc21xml
from invenio_records_resources.services.records.results import RecordItem
from sqlalchemy.orm.exc import NoResultFound

from .convert import LOM2Marc21


def oer_create_in_alma_func(
    identity: Identity,
    lom_id: str,
    alma_service: AlmaRESTService,
) -> RecordItem:
    """Export OER to Alma."""
    lom_service = current_records_lom.records_service

    if is_duplicate_in_alma(lom_id):
        msg = f"WARNING: duplicat in alma lom_id: {lom_id}"
        raise RuntimeWarning(msg)

    try:
        record = lom_service.read(identity, lom_id)
    except (NoResultFound, PIDDoesNotExistError) as error:
        msg = f"ERROR: lom_id: {lom_id} not found in db"
        raise RuntimeError(msg) from error

    # check if alma pids exists
    alma_pid = record.pids.get("alma", None)

    marc21_record = Marc21Metadata()
    lom_to_marc21 = LOM2Marc21()

    # TODO: check what record is, visit would need a dict
    lom_to_marc21.visit(record, marc21_record)

    marc21_record_etree = convert_json_to_marc21xml(marc21_record.json["metadata"])

    try:
        if alma_pid:
            alma_service.update_alma_record(mmsid=alma_pid)
        else:
            alma_record = alma_service.create_record(marc21_record_etree)

            # update repo record with new alma pid
            record.pids["alma"] = alma_record.get("mmsid")

    except AlmaRESTError as error:
        msg = f"ERROR: alma rest error on lom_id: {lom_id}, error: {error}"
        raise RuntimeError(msg) from error


def oer_create_aggregator() -> list[tuple[str, str]]:
    """OER create aggregator."""
