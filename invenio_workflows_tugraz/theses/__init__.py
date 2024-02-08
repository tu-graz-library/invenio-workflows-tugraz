# -*- coding: utf-8 -*-
#
# Copyright (C) 2022-2024 Graz University of Technology.
#
# invenio-workflows-tugraz is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Theses Workflows."""

from .theses import (
    duplicate_func,
    import_func,
    theses_create_aggregator,
    theses_filter,
    update_func,
)
from .views import create_blueprint

__all__ = (
    "theses_create_aggregator",
    "theses_filter",
    "duplicate_func",
    "import_func",
    "update_func",
    "create_blueprint",
)
