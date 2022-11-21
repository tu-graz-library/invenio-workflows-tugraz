# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Graz University of Technology.
#
# invenio-workflows-tugraz is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Theses Workflows."""

from invenio_campusonline import ThesesFilter, ThesesState


def theses_filter_for_locked_records():
    """This function returns a tuple.
    FILTER: xml filter to get locked records
    STATE: [open, locked]
    return ThesesFilter"""

    filter_ = [
        """<bas:thesesType>ALL</bas:thesesType>""",
        """<bas:state name="LOCKED"/>""",
    ]
    state = ThesesState.LOCKED
    return ThesesFilter(filter_, state)


def theses_filter_for_open_records():
    """This function returns a list of tuples.
    FILTER: xml filter to get open records
    STATE: [open, locked]
    return ThesesFilter"""
    filter_ = [
        """<bas:thesesType>ALL</bas:thesesType>""",
        """<bas:state name="IFG"/>""",
    ]
    state = ThesesState.OPEN
    return ThesesFilter(filter_, state)
