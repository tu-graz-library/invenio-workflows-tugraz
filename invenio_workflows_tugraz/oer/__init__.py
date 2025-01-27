# -*- coding: utf-8 -*-
#
# Copyright (C) 2025 Graz University of Technology.
#
# invenio-workflows-tugraz is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Convert from LOM to Marc21."""


from .workflow import oer_create_aggregator, oer_create_in_alma_func

__all__ = (
    "oer_create_aggregator",
    "oer_create_in_alma_func",
)
