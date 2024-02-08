# -*- coding: utf-8 -*-
#
# Copyright (C) 2024 Graz University of Technology.
#
# invenio-workflows-tugraz is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Models for theses workflow."""

from invenio_db import db
from sqlalchemy import BOOLEAN
from sqlalchemy_utils import UUIDType


class WorkflowThesesMetadata(db.Model):
    """Workflow theses."""

    __tablename__ = "workflows_theses"

    id = db.Column(UUIDType, primary_key=True)

    cms_id = db.Column(db.Integer)

    archived = db.Column(BOOLEAN, default=False)

    published = db.Column(BOOLEAN, default=False)

    ready_to_archive = db.Column(BOOLEAN, default=False)

    ready_to_publish = db.Column(BOOLEAN, default=False)
