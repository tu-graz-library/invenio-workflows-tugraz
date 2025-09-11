# -*- coding: utf-8 -*-
#
# Copyright (C) 2025 Graz University of Technology.
#
# invenio-workflows-tugraz is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""CLI for migrating diglib to repository."""

from pathlib import Path
from time import sleep
from typing import Literal
from xml.etree import ElementTree as ET

from click import Path as ClickPath
from click import group, option, secho
from flask.cli import with_appcontext
from invenio_access.permissions import system_identity
from invenio_catalogue_marc21.proxies import current_catalogue_marc21
from invenio_records_marc21 import Marc21Metadata, create_record

from .convert import MabToMarc21

type PID = str
type DirectoryName = str
type UbtugIds = list[str]


def wait() -> None:
    """Wait."""
    response = input("Are you ready to proceed? (yes/no): ")
    while response.lower().strip() not in ["yes", "y"]:
        if response in ["no", "n"]:
            response = input("Please fix the issue and try again. Ready? (yes/no): ")
        else:
            response = input("Please answer 'yes' or 'no': ")


def process_id(
    input_file: Path,
    directory_files: Path,
    directory_ids: Path,
    root_id: PID = "",
    parent_id: PID = "",
    publisher: str = "",
    file_access: Literal["public", "restricted"] = "restricted",
) -> PID:
    """Process id."""
    records_service = current_catalogue_marc21.records_service

    tree = ET.parse(input_file)  # noqa: S314
    root = tree.getroot()

    metadata = Marc21Metadata()
    convert = MabToMarc21(metadata, publisher)

    try:
        convert.convert(root, metadata)
    except Exception as error:
        secho(f"process_id input_file: {input_file}", fg="yellow")
        raise error from error

    level_directory_base = (
        directory_files / convert.directory_name
        if convert.directory_name
        else directory_files
    )

    is_file = False
    if convert.filename:
        base = (
            directory_files
            if convert.resource_type == "issue"
            else level_directory_base
        )
        file_path = base / f"{convert.filename}.pdf"

        while not is_file:
            is_file = file_path.exists()
            if not is_file:
                secho(
                    f"file path: {file_path} doesn't exists, look input_file: {input_file}",
                    fg="yellow",
                )
                wait()

    file_paths = [file_path] if is_file else []

    # only the root node in openlib has the access setting, all child notes have
    # to inherit it
    if convert.access != "N/A":
        file_access = convert.access

    data = {
        "metadata": metadata.json["metadata"],
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
            file_access,
        )

    sleep(1)
    record = records_service.publish(system_identity, draft.id)

    return record.id


@group("migration")
@with_appcontext
def migration_group() -> None:
    """CLI."""


@migration_group.command("import")
@option("--input-file", type=ClickPath(file_okay=True, dir_okay=False))
@option(
    "--directory-files",
    type=ClickPath(file_okay=False, dir_okay=True, path_type=Path),
)
@option(
    "--directory-ids",
    type=ClickPath(file_okay=False, dir_okay=True, path_type=Path),
)
def import_from_diglib(
    input_file: Path,
    directory_files: Path,
    directory_ids: Path,
) -> None:
    """Import from diglib."""
    record_id = process_id(input_file, directory_files, directory_ids)
    secho(
        f"input_file {input_file} successfully imported to record: {record_id}",
        fg="green",
    )
