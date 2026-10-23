# SPDX-FileCopyrightText: 2025-2026 Graz University of Technology.
# SPDX-License-Identifier: MIT

"""Convert from LOM to Marc21."""

from .workflow import oer_create_aggregator, oer_create_in_alma_func

__all__ = (
    "oer_create_aggregator",
    "oer_create_in_alma_func",
)
