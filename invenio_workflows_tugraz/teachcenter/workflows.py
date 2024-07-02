# -*- coding: utf-8 -*-
#
# Copyright (C) 2024 Graz University of Technology.
#
# invenio-workflows-tugraz is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Teachcenter workflows."""


from pathlib import Path

from flask_principal import Identity
from invenio_moodle import MoodleRESTService
from invenio_pidstore.errors import PIDDoesNotExistError
from invenio_pidstore.models import PersistentIdentifier
from invenio_records_lom.proxies import current_records_lom
from invenio_records_lom.services import LOMRecordService
from invenio_records_lom.utils import LOMRecordData, create_record, update_record
from invenio_records_resources.services.records.results import RecordItem

from .types import BaseRecord, FileKey, FileRecord, Key, LinkKey, LinkRecord, Status
from .visitor import TeachCenterToLOM


def create_key(tc_record: dict) -> Key:
    """Create key."""
    # TODO implement LinkKey (opencast)
    return FileKey(tc_record)


def create_draft(
    identity: Identity,
    key: Key,
    moodle_pid_value: str,
    records_service: LOMRecordService,
) -> RecordItem:
    """Create draft with empty metadata."""
    pids = {
        "moodle": {
            "provider": "moodle",
            "identifier": moodle_pid_value,
        },
    }
    data = LOMRecordData(resource_type=key.resource_type, pids=pids)
    data.metadata.append_identifier(moodle_pid_value, catalog="moodle")
    return records_service.create(data=data.json, identity=identity)


def get_from_database_or_create(
    identity: Identity,
    key: Key,
    records_service: LOMRecordService,
) -> BaseRecord:
    """Fetch moodle-result corresponding to `key`, create database-entry if none exists.

    :param Key key: the key which to attempt fetching from pidstore


    File:
    A File could be already in database. A File should not be added twice and it
    is looked up by its file hash (hash_sha1). If it is there already it will be
    linked to the new Unit where it is used.

    """
    moodle_pid_value = key.get_moodle_pid_value()

    try:
        moodle_pid = PersistentIdentifier.get(
            pid_type="moodle",
            pid_value=moodle_pid_value,
        )
    except PIDDoesNotExistError:
        draft = create_draft(identity, key, moodle_pid_value, records_service)
        pid = draft.id
        data = LOMRecordData(**draft.to_dict())
        status = Status.NEW
    else:
        # get lomid corresponding to moodle_pid
        lom_pid = PersistentIdentifier.get_by_object(
            pid_type="lomid",
            object_type=moodle_pid.object_type,
            object_uuid=moodle_pid.object_uuid,
        )

        pid = lom_pid.pid_value
        draft = records_service.edit(id_=pid, identity=identity)
        data = LOMRecordData(**draft.to_dict())
        status = Status.EDIT

    match key:
        case FileKey():
            type_of_record = FileRecord
        case LinkKey():
            type_of_record = LinkRecord

    return type_of_record(key, pid, data, status, draft)


def is_duplicate(draft: RecordItem, new_course_ids: list[str]) -> bool:
    """Check about duplicate."""
    try:
        existing_course_ids = [
            identifier["entry"]["langstring"]["#text"]
            for course in draft["metadata"]["courses"]
            for identifier in course["course"]["identifier"]
        ]
    except KeyError:
        existing_course_ids = []

    return any(id_ in existing_course_ids for id_ in new_course_ids)


def teachcenter_import_func(  # noqa: C901
    identity: Identity,
    tc_record: dict,
    moodle_service: MoodleRESTService,
    *,
    dry_run: bool = False,
) -> None:
    """Insert data encoded in `moodle-data` into invenio-database.

    :param dict moodle_data: The data to be inserted into database,
        whose format matches `MoodleSchema`
    :param Identity identity
    """
    records_service = current_records_lom.records_service

    record_key = create_key(tc_record)
    draft = get_from_database_or_create(identity, record_key, records_service)

    visitor = TeachCenterToLOM()
    visitor.visit(tc_record, draft.data.metadata)

    file_url = visitor.file_url

    file_paths = []
    if isinstance(draft, FileRecord) and draft.status == Status.NEW:
        file_paths += [moodle_service.download_file(identity, file_url)]

    if dry_run:
        if draft.status == Status.NEW:
            records_service.delete_draft(id_=draft.draft.id, identity=identity)
        if len(file_paths):
            for file_path in file_paths:
                Path(file_path).unlink()
        msg = f"DRY_RUN teachcenter import success id: {record_key}"
        raise RuntimeError(msg)

    match draft.status:
        case Status.NEW:
            create_record(records_service, draft.data.json, file_paths, identity)
        case Status.EDIT:
            if is_duplicate(draft.draft, visitor.course_ids):
                msg = f"WARNING course already in record pid: {draft.pid}"
                raise RuntimeError(msg)

            data = draft.draft.data
            for course in draft.data.metadata.get_courses():
                if course not in data["metadata"]["courses"]:
                    data["metadata"]["courses"].append(course)

            update_record(draft.pid, records_service, data, identity)
