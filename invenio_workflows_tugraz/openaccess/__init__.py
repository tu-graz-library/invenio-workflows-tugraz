# -*- coding: utf-8 -*-
#
# Copyright (C) 2022-2025 Graz University of Technology.
#
# invenio-workflows-tugraz is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Open Access Workflow."""

from .config import WorkflowOpenaccessServiceConfig
from .service import WorkflowOpenaccessService
from .workflow import (
    openaccess_filter,
    openaccess_import_func,
    openaccess_mark_as_exported_aggregator,
    openaccess_update_status_in_pure,
)

__all__ = (
    "WorkflowOpenaccessService",
    "WorkflowOpenaccessServiceConfig",
    "openaccess_filter",
    "openaccess_import_func",
    "openaccess_mark_as_exported_aggregator",
    "openaccess_update_status_in_pure",
)
