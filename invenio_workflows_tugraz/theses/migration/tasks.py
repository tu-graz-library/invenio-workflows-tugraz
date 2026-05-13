# -*- coding: utf-8 -*-
#
# Copyright (C) 2026 Graz University of Technology.
#
# invenio-workflows-tugraz is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Thesis migration task.

using a task makes it easier to run it as a background job.
"""

from celery import shared_task
from invenio_db import db
from invenio_pidstore.errors import PIDAlreadyExists
from invenio_pidstore.models import PersistentIdentifier
from invenio_records_marc21.proxies import current_records_marc21
from invenio_records_marc21.records import Marc21Draft, Marc21Record
from invenio_records_marc21.services.record.metadata import Marc21Metadata

from ..pids.providers import CMSPIDProvider


@shared_task(ignore_result=True)
def update_pids(recid: str) -> None:
    """Update pid."""
    try:
        record = Marc21Record.get_record(recid)
    except Exception:  # noqa: BLE001
        record = Marc21Draft.get_record(recid)

    pids: list[tuple[PersistentIdentifier, str] | tuple[None, None]] = []

    pids.append(update_pids_cms(record))

    update_record(record, pids)
    db.session.commit()


def update_pids_cms(
    record: Marc21Record | Marc21Draft,
) -> tuple[PersistentIdentifier, str] | tuple[None, None]:
    """Update pids."""
    if record.is_deleted:
        return None, None

    provider: CMSPIDProvider = (
        current_records_marc21.records_service.config.pids_providers["cms"]["cms"]
    )

    metadata = Marc21Metadata(json=record.metadata)

    try:
        pid_value = metadata.get_field("995...a")["subfields"]["a"][0]
    except (AttributeError, IndexError, TypeError):
        return None, None

    try:
        pid = provider.create(record=record, pid_value=pid_value)
    except PIDAlreadyExists as error:
        pid = PersistentIdentifier.get(error.pid_type, error.pid_value)

    return pid, provider.name


def update_record(
    record: Marc21Record | Marc21Draft,
    pids: list[tuple[PersistentIdentifier, str] | tuple[None, None]],
) -> None:
    """Update Record."""
    if len(pids) == 0:
        return

    are_changes = False

    for pid, provider_name in pids:
        if not pid:
            continue

        if pid.pid_type in record["pids"]:
            continue

        record["pids"][pid.pid_type] = {
            "identifier": pid.pid_value,
            "provider": provider_name,
        }
        are_changes = True

    if are_changes:
        record.commit()
