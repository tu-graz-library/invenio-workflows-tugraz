# -*- coding: utf-8 -*-
#
# Copyright (C) 2025-2026 Graz University of Technology.
#
# invenio-workflows-tugraz is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""CLI for migrating diglib to repository."""

from pathlib import Path
from time import sleep
from typing import Literal
from xml.etree import ElementTree as ET

from click import BOOL
from click import Path as ClickPath
from click import group, option, secho
from flask.cli import with_appcontext
from invenio_access.permissions import system_identity
from invenio_alma.proxies import current_alma
from invenio_alma.services.errors import AlmaAPIError
from invenio_catalogue_marc21.proxies import current_catalogue_marc21
from invenio_pidstore.models import PersistentIdentifier
from invenio_rdm_records.services.errors import ValidationErrorWithMessageAsList
from invenio_records_marc21 import (
    Marc21Metadata,
    convert_marc21xml_to_json,
    create_record,
)
from sqlalchemy.exc import NoResultFound

from .convert import MabToMarc21

type PID = str


def wait() -> None:
    """Wait."""
    response = input("Are you ready to proceed? (yes/no): ")
    while response.lower().strip() not in ["yes", "y"]:
        if response in ["no", "n"]:
            response = input("Please fix the issue and try again. Ready? (yes/no): ")
        else:
            response = input("Please answer 'yes' or 'no': ")


def process_id(  # noqa: C901 PLR0915 PLR0917
    input_file: Path,
    directory_files: Path,
    directory_ids: Path,
    root_id: PID = "",
    parent_id: PID = "",
    publisher: str = "",
    publication_year: str = "",
    file_access: Literal["public", "restricted"] = "restricted",
    *,
    production: bool = False,
) -> PID:
    """Process id."""
    records_service = current_catalogue_marc21.records_service
    alma_sru_service = current_alma._alma_sru_service  # noqa: SLF001

    tree = ET.parse(input_file)  # noqa: S314
    root = tree.getroot()

    metadata = Marc21Metadata()
    convert = MabToMarc21(metadata, publisher, publication_year, production=production)

    try:
        convert.convert(root, metadata)
    except Exception as error:
        secho(f"process_id input_file: {input_file}", fg="yellow")
        raise error from error

    # if there exists a isbn or ac number which can be used to get metadata from
    # alma please use that metadata, otherwise ignore that path and use the
    # converted metadata
    try:
        if convert.isbn != "":
            metadata_xml = alma_sru_service.get_record(
                search_value=convert.isbn,
                search_key="isbn",
            )
            metadata = Marc21Metadata(json=convert_marc21xml_to_json(metadata_xml))

        if convert.ac_number != "":
            metadata_xml = alma_sru_service.get_record(
                search_value=convert.isbn,
                search_key="other_system_number",
            )
            metadata = Marc21Metadata(json=convert_marc21xml_to_json(metadata_xml))
    except AlmaAPIError:

        pass

    level_directory_base = (
        directory_files / convert.directory_name
        if convert.directory_name
        else directory_files
    )

    file_paths: list[Path] = []
    if convert.filename:
        base = (
            directory_files
            if convert.resource_type == "issue"
            else level_directory_base
        )
        file_path = base / f"{convert.filename}.pdf"

        while not file_path.exists():
            secho(
                f"file path: {file_path} doesn't exists, look input_file: {input_file}",
                fg="yellow",
            )
            wait()

        file_paths.append(file_path)

    # only the root node in openlib has the access setting, all child notes have
    # to inherit it
    if convert.access != "N/A":
        file_access = convert.access

    data = {
        "metadata": metadata.json["metadata"],
        "pids": {
            "odi": {
                "provider": "legacy",
                "identifier": input_file.stem,
            },
        },
        "files": {"enabled": bool(file_paths)},
        "access": {
            "files": file_access,
            "record": "public",
        },
        "catalogue": {
            "root": root_id,
            "parent": parent_id,
            "children": [],
        },
        "children": [],
    }

    try:
        draft = create_record(
            service=records_service,
            data=data,
            file_paths=file_paths,
            identity=system_identity,
            do_publish=False,
        )

    except ValidationErrorWithMessageAsList:
        pid = PersistentIdentifier.get(pid_type="odi", pid_value=input_file.stem)

        try:
            tmp_draft = records_service.draft_cls.get_record(pid.object_uuid)
            draft = records_service.edit(system_identity, tmp_draft.pid.pid_value)
        except NoResultFound:
            record = records_service.record_cls.get_record(pid.object_uuid)
            draft = records_service.edit(system_identity, record.pid.pid_value)

        records_service.update_draft(system_identity, draft.id, data)

    except Exception as error:
        secho(f"error: {error} process_id input_file: {input_file}", fg="red")
        raise error from error

    # TODO:
    # validate draft, if it doesn't validate rollback the current import session

    root_id = root_id or draft.id
    parent_id = draft.id

    for child_id in convert.children_ids:
        child_filename = directory_ids / f"{child_id}.xml"
        process_id(
            child_filename,
            level_directory_base,
            directory_ids,
            root_id,
            parent_id,
            convert.publisher,
            convert.year,
            file_access,
            production=production,
        )

    # TODO: set the custom publisher doi in pidstore_pid to registered, then the publish should update the url automatically
    sleep(1)

    # do this only in production. locally please not, because otherwise testing
    # would not be possible anymore
    if production:
        pid = PersistentIdentifier.get(pid_type="publ", pid_value=convert.doi)
        # with this hack it is possible to update the dois on datacite directly.
        # normally the pid status would be "N" which says to the provider please
        # register it, but that part would fail since the doi is registered
        # already, but with "R" it says please update me, and we want this!
        pid.status = "R"

    record = records_service.publish(system_identity, draft.id)
    secho(f"record {record.id} is published", fg="green")
    return record.id


@group("migration")
@with_appcontext
def migration_group() -> None:
    """CLI."""


@migration_group.command("import")
@option("--input-file", type=ClickPath(file_okay=True, dir_okay=False, path_type=Path))
@option(
    "--directory-files",
    type=ClickPath(file_okay=False, dir_okay=True, path_type=Path),
)
@option(
    "--directory-ids",
    type=ClickPath(file_okay=False, dir_okay=True, path_type=Path),
)
@option(
    "--base",
    type=ClickPath(file_okay=False, dir_okay=True, path_type=Path),
    default=None,
)
@option("--is-production", type=BOOL, is_flag=True, default=False)
def import_from_diglib(
    input_file: Path,
    directory_files: Path,
    directory_ids: Path,
    base: Path,
    *,
    is_production: bool,
) -> None:
    """Import from diglib."""
    if base:
        filename = list(base.parts)[-1]
        input_file = base / f"{filename}.xml"
        directory_ids = base
        directory_files = base

    record_id = process_id(
        input_file,
        directory_files,
        directory_ids,
        production=is_production,
    )
    secho(
        f"input_file {input_file} successfully imported to record: {record_id}",
        fg="green",
    )
