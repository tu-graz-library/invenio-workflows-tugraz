# -*- coding: utf-8 -*-
#
# Copyright (C) 2022-2025 Graz University of Technology.
#
# invenio-workflows-tugraz is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Open Access Workflow."""

from .workflow import openaccess_filter, openaccess_import_func

__all__ = (
    "openaccess_filter",
    "openaccess_import_func",
)
