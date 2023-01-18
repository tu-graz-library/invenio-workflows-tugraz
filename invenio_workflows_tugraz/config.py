# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Graz University of Technology.
#
# invenio-workflows-tugraz is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""This is the configuration file."""

from .openaccess import pure_import_func, pure_sieve_func
from .theses import (
    import_func,
    theses_create_aggregator,
    theses_filter_for_locked_records,
    theses_filter_for_open_records,
)

WORKFLOW_ALMA_REPOSITORY_RECORDS_UPDATE_AGGREGATORS = []
""""""

WORKFLOW_ALMA_ALMA_RECORDS_CREATE_AGGREGATORS = [
    theses_create_aggregator,
]
""""""

WORKFLOW_CAMPUSONLINE_THESES_FILTERS = [
    theses_filter_for_locked_records(),
    theses_filter_for_open_records(),
]
""""""

WORKFLOW_CAMPUSONLINE_IMPORT_FUNC = import_func


WORKFLOW_PURE_IMPORT_FUNC = pure_import_func
"""See corresponding varaible in invenio-pure."""

WORKFLOW_PURE_SIEVE_FUNC = pure_sieve_func
