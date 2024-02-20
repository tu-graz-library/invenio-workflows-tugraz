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


class WorkflowThesesMetadata(db.Model):
    """Workflow theses."""

    __tablename__ = "workflows_theses"

    pid = db.Column(db.String(255), primary_key=True)

    cms_id = db.Column(db.Integer)

    imported_in_repo = db.Column(BOOLEAN, default=False)

    archived_in_cms = db.Column(BOOLEAN, default=False)

    created_in_alma = db.Column(BOOLEAN, default=False)

    updated_in_repo = db.Column(BOOLEAN, default=False)

    published_in_cms = db.Column(BOOLEAN, default=False)
