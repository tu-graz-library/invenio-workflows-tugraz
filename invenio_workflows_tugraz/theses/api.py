# -*- coding: utf-8 -*-
#
# Copyright (C) 2024 Graz University of Technology.
#
# invenio-workflows-tugraz is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""API for theses workflow."""

from invenio_db import db
from invenio_records.api import Record

from .models import WorkflowThesesMetadata


class WorkflowTheses(Record):
    """Workflow thesis api."""

    model_cls = WorkflowThesesMetadata

    @classmethod
    def create(cls, id_: str, cms_id: str) -> WorkflowThesesMetadata:
        """Create."""
        entry = cls.model_cls(id=id_, cms_id=cms_id, ready_to_archive=True)
        db.session.add(entry)
        db.session.commit()
        return entry

    @classmethod
    def set_ready_to(cls, id_: str, state: str) -> None:
        """Set is ready."""
        record = cls.model_cls.query.filter_by(id=id_)
        if state == "archive":
            record.ready_to_archive = True
        if state == "publish":
            record.ready_to_publish = True

    @classmethod
    def set_state(cls, id_: str, state: str) -> None:
        """Set archived."""
        record = cls.model_cls.query.filter_by(id=id_)
        if state == "archived":
            record.archived = True
        if state == "published":
            record.published = True

    @classmethod
    def get_ready_to(cls, state: str) -> list[tuple[str, str]]:
        """Get ready to."""
        entries = []
        if state == "archive":
            entries = cls.model_cls.query.filter_by(
                ready_to_archive=True,
                archived=False,
            )
        if state == "publish":
            entries = cls.model_cls.query.filter_by(
                ready_to_publish=True,
                published=False,
            )

        return [(entry.id, entry.cms_id) for entry in entries]
