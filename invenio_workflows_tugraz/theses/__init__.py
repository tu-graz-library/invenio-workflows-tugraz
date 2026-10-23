# SPDX-FileCopyrightText: 2022-2026 Graz University of Technology.
# SPDX-License-Identifier: MIT

"""Theses Workflows."""

from .config import WorkflowThesesServiceConfig
from .service import WorkflowThesesService
from .theses import (
    theses_create_aggregator,
    theses_create_func,
    theses_filter,
    theses_import_from_alma_func,
    theses_import_from_cms_func,
    theses_update_aggregator,
    theses_update_func,
)
from .views import create_blueprint

__all__ = (
    "WorkflowThesesService",
    "WorkflowThesesServiceConfig",
    "create_blueprint",
    "theses_create_aggregator",
    "theses_create_func",
    "theses_filter",
    "theses_import_from_alma_func",
    "theses_import_from_cms_func",
    "theses_update_aggregator",
    "theses_update_func",
)
