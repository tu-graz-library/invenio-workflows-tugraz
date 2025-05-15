# -*- coding: utf-8 -*-
#
# Copyright (C) 2025 Graz University of Technology.
#
# invenio-workflows-tugraz is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Models for theses workflow."""

from invenio_db import db
from invenio_records.models import Timestamp
from sqlalchemy import BOOLEAN


class WorkflowOpenaccessMetadata(db.Model, Timestamp):
    """Workflow theses."""

    __tablename__ = "workflows_openaccess"

    pid = db.Column(db.String(255), primary_key=True)

    pure_id = db.Column(db.String(255))

    imported_in_repo = db.Column(BOOLEAN, default=False)

    marked_as_exported = db.Column(BOOLEAN, default=False)
