# -*- coding: utf-8 -*-
#
# Copyright (C) 2022-2024 Graz University of Technology.
#
# invenio-workflows-tugraz is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Configuration file."""

from .openaccess import pure_import_func, pure_sieve_func
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

WORKFLOW_ALMA_REPOSITORY_RECORDS_IMPORT_FUNC = import_from_alma_func
""""""

WORKFLOW_ALMA_REPOSITORY_RECORDS_UPDATE_AGGREGATOR = theses_update_aggregator
""""""

WORKFLOW_ALMA_REPOSITORY_RECORDS_UPDATE_FUNC = update_func
""""""

WORKFLOW_ALMA_ALMA_RECORDS_CREATE_FUNC = create_func
""""""

WORKFLOW_ALMA_ALMA_RECORDS_CREATE_AGGREGATOR = theses_create_aggregator
""""""

WORKFLOW_CAMPUSONLINE_THESES_FILTER = theses_filter()
""""""

WORKFLOW_CAMPUSONLINE_IMPORT_FUNC = import_from_cms_func
""""""

WORKFLOW_CAMPUSONLINE_DUPLICATE_FUNC = duplicate_func
""""""

WORKFLOW_PURE_IMPORT_FUNC = pure_import_func
"""See corresponding varaible in invenio-pure."""

WORKFLOW_PURE_SIEVE_FUNC = pure_sieve_func
