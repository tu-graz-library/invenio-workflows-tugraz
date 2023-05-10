# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Graz University of Technology.
#
# invenio-workflows-tugraz is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Open Access Workflow."""
from collections.abc import Callable

from invenio_config_tugraz import get_identity_from_user_by_email
from invenio_pure import PureConfigs, PureRecord
from invenio_records_marc21 import (
    DuplicateRecordError,
    Marc21Metadata,
    check_about_duplicate,
    create_record,
    current_records_marc21,
)
from invenio_records_resources.services.records.results import RecordItem

from .convert import Pure2Marc21
from .types import PureId
from .utils import (
    access_type,
    extract_file_url,
    extract_pure_id,
    license_type,
    workflow,
)


def pure_import_func(
    pure_record: PureRecord,
    configs: PureConfigs,
    download_file: Callable,
) -> RecordItem:
    """Import record from pure into the repository."""
    pure_id = extract_pure_id(pure_record)
    file_urls = extract_file_url(pure_record)

    file_paths = []
    for i, file_url in enumerate(file_urls):
        file_path = download_file(
            f"{pure_id}-{i}",
            file_url,
            configs.pure_username,
            configs.pure_password,
        )
        file_paths.append(file_path)

    marc21_record = Marc21Metadata()
    convert = Pure2Marc21()
    convert.convert(pure_record, marc21_record)

    identity = get_identity_from_user_by_email(email=configs.user_email)
    service = current_records_marc21.records_service
    data = marc21_record.json
    data["access"] = {"record": "public", "files": "public"}

    return create_record(service, data, file_paths, identity, do_publish=True)


def pure_sieve_func(pure_record: PureRecord) -> bool:
    """Check if the record fullfills the import criteria."""
    try:
        pure_id = extract_pure_id(pure_record)
        check_about_duplicate(PureId(pure_id))
        duplicate_sieve = True
    except DuplicateRecordError:
        return False

    file_sieve = False
    for electronic_version in pure_record["electronicVersions"]:
        if (
            "file" in electronic_version
            and access_type(electronic_version) in ["Open", "Offen"]
            and license_type(electronic_version).startswith("CC BY")
            and workflow(pure_record["workflow"]) in ["Valid"]
        ):
            file_sieve = True

    return duplicate_sieve and file_sieve
