# -*- coding: utf-8 -*-
#
# Copyright (C) 2022-2024 Graz University of Technology.
#
# invenio-workflows-tugraz is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Theses Workflows."""

from .config import WorkflowThesesServiceConfig
from .service import WorkflowThesesService
from .theses import (
    create_func,
    duplicate_func,
    import_from_alma_func,
    import_from_cms_func,
    theses_create_aggregator,
    theses_filter,
    theses_update_aggregator,
    update_func,
)
from .views import create_blueprint

__all__ = (
    "theses_create_aggregator",
    "theses_update_aggregator",
    "theses_filter",
    "duplicate_func",
    "import_from_alma_func",
    "import_from_cms_func",
    "update_func",
    "create_func",
    "create_blueprint",
    "WorkflowThesesServiceConfig",
    "WorkflowThesesService",
)
