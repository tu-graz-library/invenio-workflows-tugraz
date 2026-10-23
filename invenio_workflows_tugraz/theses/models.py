# SPDX-FileCopyrightText: 2024-2026 Graz University of Technology.
# SPDX-License-Identifier: MIT

"""Models for theses workflow."""

from invenio_db import db
from sqlalchemy import BOOLEAN


class WorkflowThesesMetadata(db.Model):  # type: ignore[name-defined, misc]
    """Workflow theses."""

    __tablename__ = "workflows_theses"

    pid: str = db.Column(db.String(255), primary_key=True)

    cms_id: int = db.Column(db.Integer)

    imported_in_repo = db.Column(BOOLEAN, default=False)

    archived_in_cms = db.Column(BOOLEAN, default=False)

    created_in_alma = db.Column(BOOLEAN, default=False)

    updated_in_repo = db.Column(BOOLEAN, default=False)

    published_in_cms = db.Column(BOOLEAN, default=False)
