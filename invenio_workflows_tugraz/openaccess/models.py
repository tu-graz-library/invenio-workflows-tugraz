# SPDX-FileCopyrightText: 2025-2026 Graz University of Technology.
# SPDX-License-Identifier: MIT

"""Models for theses workflow."""

from invenio_db import db
from sqlalchemy import BOOLEAN


class WorkflowOpenaccessMetadata(db.Model, db.Timestamp):  # type: ignore[name-defined, misc]
    """Workflow theses."""

    __tablename__ = "workflows_openaccess"

    pid: str = db.Column(db.String(255), primary_key=True)

    pure_id: str = db.Column(db.String(255))

    imported_in_repo: bool = db.Column(BOOLEAN, default=False)

    marked_as_exported: bool = db.Column(BOOLEAN, default=False)
