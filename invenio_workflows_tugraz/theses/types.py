# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Graz University of Technology.
#
# invenio-workflows-tugraz is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Theses Workflows."""


from invenio_records_marc21.services.record.types import Marc21Category


class CampusOnlineId(Marc21Category):
    """Campus online ID."""

    category: str = "995.subfields.d.keyword"
