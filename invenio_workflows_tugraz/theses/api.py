# -*- coding: utf-8 -*-
#
# Copyright (C) 2024 Graz University of Technology.
#
# invenio-workflows-tugraz is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""API for theses workflow."""

from __future__ import annotations

from invenio_db import db

from .models import WorkflowThesesMetadata


class WorkflowTheses:
    """Workflow thesis api."""

    model_cls = WorkflowThesesMetadata

    def __init__(self, model: WorkflowThesesMetadata = None) -> None:
        """Construct WorkflowTheses."""
        self.model = model

    @property
    def pid(self) -> str:
        """Get Pid."""
        return self.model.pid

    @property
    def cms_id(self) -> str:
        """Get cms_id."""
        return self.model.cms_id

    @classmethod
    def resolve(cls, id_: str):  # noqa: ANN206
        """Get."""
        model = cls.model_cls.query.filter_by(pid=id_).one_or_none()
        return cls(model=model)

    @classmethod
    def create(cls, id_: str, cms_id: str):  # noqa: ANN206
        """Create."""
        with db.session.begin_nested():
            entry = cls(model=cls.model_cls(pid=id_, cms_id=cms_id))
            db.session.add(entry.model)
        return entry

    def commit(self) -> None:
        """Commit."""
        with db.session.begin_nested():
            db.session.merge(self.model)

    def set_state(self, state: str) -> None:
        """Set archived."""
        if state == "archived_in_cms":
            self.model.archived_in_cms = True
        if state == "imported_in_repo":
            self.model.imported_in_repo = True
        if state == "created_in_alma":
            self.model.created_in_alma = True
        if state == "updated_in_repo":
            self.model.updated_in_repo = True
        if state == "published_in_cms":
            self.model.published_in_cms = True
        db.session.merge(self.model)

    @classmethod
    def get_ready_to(cls, state: str) -> list:
        """Get ready to."""
        entries = []
        if state == "archive_in_cms":
            entries = cls.model_cls.query.filter_by(
                imported_in_repo=True,
                archived_in_cms=False,
            )

        if state == "create_in_alma":
            entries = cls.model_cls.query.filter_by(
                archived_in_cms=True,
                created_in_alma=False,
            )

        if state == "update_in_repo":
            entries = cls.model_cls.query.filter_by(
                created_in_alma=True,
                updated_in_repo=False,
            )

        if state == "publish_in_cms":
            entries = cls.model_cls.query.filter_by(
                updated_in_repo=True,
                published_in_cms=False,
            )

        return [cls(model=entry) for entry in entries.all()]
