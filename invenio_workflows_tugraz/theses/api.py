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
    def get(cls, id_: str):
        """Get."""
        return cls.model_cls.query.filter_by(pid=id_).one_or_none()

    @classmethod
    def create(cls, id_: str, cms_id: str) -> WorkflowThesesMetadata:
        """Create."""
        entry = cls.model_cls(pid=id_, cms_id=cms_id)
        return entry

    def set_state(self, id_: str, state: str) -> None:
        """Set archived."""
        if state == "archived_in_cms":
            self.model.archived_in_cms = True
        if state == "created_in_alma":
            self.model.created_in_alma = True
        if state == "published_in_cms":
            self.model.published_in_cms = True
        db.session.merge(self.model)

    def set_ready_to(self, id_: str, state: str) -> None:
        """Set is ready."""
        if state == "archive_in_cms":
            self.model.ready_to_archive_in_cms = True
        if state == "create_in_alma":
            self.model.ready_to_create_in_alma = True
        if state == "update_in_repo":
            self.model.ready_to_update_in_repo = True
        if state == "publish_in_cms":
            self.model.ready_to_publish_in_cms = True
        db.session.merge(self.model)

    @classmethod
    def get_ready_to(cls, state: str) -> list[tuple[str, str]]:
        """Get ready to."""
        entries = []
        if state == "archive_in_cms":
            entries = cls.model_cls.query.filter_by(
                ready_to_archive=True,
                archived_in_cms=False,
            )

        if state == "create_in_alma":
            entries = cls.model_cls.query.filter_by(
                created_in_alma=False,
                archived_in_cms=True,
            )

        if state == "update_in_repo":
            entries = cls.model_cls.query.filter_by(
                created_in_alma=True,
                published_in_cms=False,
            )

        if state == "publish_in_cms":
            entries = cls.model_cls.query.filter_by(
                ready_to_publish=True,
                published_in_cms=False,
            )

        return [(entry.id, entry.cms_id) for entry in entries]
