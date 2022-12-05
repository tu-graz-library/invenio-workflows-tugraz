# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Graz University of Technology.
#
# invenio-workflows-tugraz is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Theses Workflows."""

from .theses import (
    import_func,
    theses_create_aggregator,
    theses_filter_for_locked_records,
    theses_filter_for_open_records,
)

__all__ = (
    "theses_create_aggregator",
    "theses_filter_for_locked_records",
    "theses_filter_for_open_records",
    "import_func",
)
