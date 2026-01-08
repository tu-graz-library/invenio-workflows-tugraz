# -*- coding: utf-8 -*-
#
# Copyright (C) 2022-2026 Graz University of Technology.
#
# invenio-workflows-tugraz is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Openaccess Workflow utils."""

from invenio_pure import URL
from invenio_records_marc21 import check_about_duplicate

from .types import PureId


@check_about_duplicate.register
def _(value: PureId) -> None:
    """Check about double pure id."""
    check_about_duplicate(str(value), value.category)


def access_type(electronic_version: dict[str, dict[str, str]]) -> str:
    """Get Access type."""
    return electronic_version.get("accessType", {}).get("uri", "")


def license_type(electronic_version: dict[str, dict[str, str]]) -> str:
    """Get license type."""
    return electronic_version.get("licenseType", {}).get("uri", "")


def extract_files(pure_record: dict) -> list[URL]:
    """Extract file url."""

    def condition(item: dict) -> bool:
        condition_1 = (
            access_type(item) == "/dk/atira/pure/core/openaccesspermission/open"
        )
        condition_2 = "cc_by" in license_type(item)
        return condition_1 and condition_2

    files: list[URL] = []
    for electronic_version in pure_record["electronicVersions"]:
        try:
            if condition(electronic_version):
                files.append(electronic_version["file"])
        except (KeyError, TypeError):
            continue

    if len(files) == 0:
        msg = f"record: {pure_record["uuid"]} doesn't provide downloadable files"
        raise RuntimeError(msg)

    return files


def change_to_exported(pure_record: dict) -> dict:
    """Replace the keyword group."""
    replaced = False
    for keyword_group in pure_record["keywordGroups"]:
        if (
            keyword_group["logicalName"]
            == "dk/atira/pure/researchoutput/keywords/export2repo"
        ):
            replaced = True
            keyword_group["classifications"] = [
                {
                    "uri": "dk/atira/pure/researchoutput/keywords/export2repo/exported",
                    "term": {
                        "en_GB": "Exported",
                        "de_DE": "Exportiert",
                    },
                },
            ]

    # necessary if the keyword group does not show up in keywordGroups due to
    # pure configuration
    if not replaced:
        keyword_group_validated = {
            "typeDiscriminator": "ClassificationsKeywordGroup",
            "pureId": 76333629,
            "logicalName": "dk/atira/pure/researchoutput/keywords/export2repo",
            "name": {
                "en_GB": "Export to Repository",
                "de_DE": "Export ins Repository",
            },
            "classifications": [
                {
                    "uri": "dk/atira/pure/researchoutput/keywords/export2repo/validated",
                    "term": {
                        "en_GB": "Validated",
                        "de_DE": "Validiert",
                    },
                },
                {
                    "uri": "dk/atira/pure/researchoutput/keywords/export2repo/exported",
                    "term": {
                        "en_GB": "Exported",
                        "de_DE": "Exportiert",
                    },
                },
            ],
        }
        pure_record["keywordGroups"].append(keyword_group_validated)

    return pure_record
