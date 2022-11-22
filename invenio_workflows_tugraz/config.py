# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Graz University of Technology.
#
# invenio-workflows-tugraz is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""This is the configuration file."""
from .theses import theses_filter_for_locked_records, theses_filter_for_open_records

WORKFLOW_ALMA_REPOSITORY_RECORDS_UPDATE_AGGREGATORS = []
""""""

WORKFLOW_ALMA_ALMA_RECORDS_CREATE_AGGREGATORS = []
""""""

WORKFLOW_CAMPUSONLINE_THESES_FILTERS = [
    theses_filter_for_locked_records(),
    theses_filter_for_open_records(),
]
""""""
