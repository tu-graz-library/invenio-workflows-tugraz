# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Graz University of Technology.
#
# invenio-workflows-tugraz is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Openaccess Workflow utils."""

from invenio_pure import URL, PureID, PureRecord, PureRuntimeError
from invenio_records_marc21 import check_about_duplicate

from .types import PureId


@check_about_duplicate.register
def _(value: PureId):
    """Check about double pure id."""
    check_about_duplicate(str(value), value.category)


def access_type(electronic_version: dict) -> str:
    """Get Access type."""
    try:
        return electronic_version["accessType"]["term"]["text"][0]["value"]
    except (KeyError, TypeError):
        return False


def license_type(electronic_version: dict) -> str:
    """Get license type."""
    try:
        return electronic_version["licenseType"]["term"]["text"][0]["value"]
    except (KeyError, TypeError):
        return False


def workflow(electronic_version: dict) -> str:
    """Get workflow status."""
    try:
        return electronic_version["workflow"]["value"]["text"][0]["value"]
    except (KeyError, TypeError):
        return False


def extract_pure_id(pure_record: PureRecord) -> PureID:
    """Extract pure id."""
    return pure_record["pureId"]


def extract_file_url(pure_record: PureRecord) -> URL:
    """Extract file url."""

    def condition(item):
        return access_type(item) in ["Open", "Offen"] and license_type(item).startswith(
            "CC BY"
        )

    file_urls = []
    for electronic_version in pure_record["electronicVersions"]:
        try:
            file_url = electronic_version["file"]["fileURL"]
            if condition(electronic_version):
                file_urls.append(file_url)
        except (KeyError, TypeError):
            continue

    if len(file_urls) == 0:
        raise PureRuntimeError(pure_record)

    return file_urls
