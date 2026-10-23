# SPDX-FileCopyrightText: 2022-2026 Graz University of Technology.
# SPDX-License-Identifier: MIT

"""Open Access Workflows."""

from invenio_records_marc21.services.record.types import Marc21Category


class PureId(Marc21Category):
    """Pure ID."""

    category: str = "024.subfields.a.keyword"
