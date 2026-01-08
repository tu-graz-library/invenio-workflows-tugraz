# -*- coding: utf-8 -*-
#
# Copyright (C) 2025-2026 Graz University of Technology.
#
# invenio-workflows-tugraz is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Models for theses workflow."""

from invenio_db import db
from sqlalchemy import BOOLEAN


class WorkflowOpenaccessMetadata(db.Model, db.Timestamp):
    """Workflow theses."""

    __tablename__ = "workflows_openaccess"

    pid: str = db.Column(db.String(255), primary_key=True)

    pure_id: str = db.Column(db.String(255))

    imported_in_repo: bool = db.Column(BOOLEAN, default=False)

    marked_as_exported: bool = db.Column(BOOLEAN, default=False)
