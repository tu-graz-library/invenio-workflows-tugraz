# -*- coding: utf-8 -*-
#
# Copyright (C) 2022-2025 Graz University of Technology.
#
# invenio-workflows-tugraz is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Theses Workflows."""

from .config import WorkflowThesesServiceConfig
from .service import WorkflowThesesService
from .theses import (
    theses_create_aggregator,
    theses_create_func,
    theses_duplicate_func,
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
    "theses_duplicate_func",
    "theses_filter",
    "theses_import_from_alma_func",
    "theses_import_from_cms_func",
    "theses_update_aggregator",
    "theses_update_func",
)
