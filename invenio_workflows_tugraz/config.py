# -*- coding: utf-8 -*-
#
# Copyright (C) 2022-2024 Graz University of Technology.
#
# invenio-workflows-tugraz is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Configuration file."""

from .imoox import imoox_import_func
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

WORKFLOWS_ALMA_REPOSITORY_RECORDS_IMPORT_FUNC = import_from_alma_func
""""""

WORKFLOWS_ALMA_REPOSITORY_RECORDS_UPDATE_AGGREGATOR = theses_update_aggregator
""""""

WORKFLOWS_ALMA_REPOSITORY_RECORDS_UPDATE_FUNC = update_func
""""""

WORKFLOWS_ALMA_ALMA_RECORDS_CREATE_FUNC = create_func
""""""

WORKFLOWS_ALMA_ALMA_RECORDS_CREATE_AGGREGATOR = theses_create_aggregator
""""""

WORKFLOWS_CAMPUSONLINE_THESES_FILTER = theses_filter()
""""""

WORKFLOWS_CAMPUSONLINE_IMPORT_FUNC = import_from_cms_func
""""""

WORKFLOWS_CAMPUSONLINE_DUPLICATE_FUNC = duplicate_func
""""""

WORKFLOWS_PURE_IMPORT_FUNC = pure_import_func
"""See corresponding varaible in invenio-pure."""

WORKFLOWS_PURE_SIEVE_FUNC = pure_sieve_func
""""""

WORKFLOWS_IMOOX_REPOSITORY_IMPORT_FUNC = imoox_import_func
""""""
