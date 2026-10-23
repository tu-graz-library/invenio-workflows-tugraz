# SPDX-FileCopyrightText: 2022-2026 Graz University of Technology.
# SPDX-License-Identifier: MIT

"""Theses Workflows."""

from invenio_records_marc21.services.record.types import Marc21Category


class CampusOnlineId(Marc21Category):
    """Campus online ID."""

    category: str = "995.subfields.a.keyword"
