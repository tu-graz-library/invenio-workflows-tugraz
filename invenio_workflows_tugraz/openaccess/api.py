# -*- coding: utf-8 -*-
#
# Copyright (C) 2024-2025 Graz University of Technology.
#
# invenio-workflows-tugraz is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""API for theses workflow."""

from __future__ import annotations

from invenio_db import db

from .models import WorkflowOpenaccessMetadata


class WorkflowOpenaccess:
    """Workflow openaccess api."""

    model_cls = WorkflowOpenaccessMetadata

    def __init__(self, model: WorkflowOpenaccessMetadata) -> None:
        """Construct WorkflowOpenaccess."""
        self.model = model

    @property
    def pid(self) -> str:
        """Get pid."""
        return self.model.pid

    @property
    def pure_id(self) -> str:
        """Get pure id."""
        return self.model.pure_id

    @classmethod
    def resolve(cls, id_: str):  # noqa: ANN206
        """Get."""
        model = cls.model_cls.query.filter_by(pid=id_).one_or_none()
        return cls(model=model)

    @classmethod
    def get_ready_to(cls, state: str) -> list:
        """Get ready to."""
        entries = []
        if state == "marked_as_exported":
            entries = cls.model_cls.query.filter_by(
                imported_in_repo=True,
            )

        return [cls(model=entry) for entry in entries.all()]

    @classmethod
    def create(cls, id_: str, pure_id: str):  # noqa: ANN206
        """Create."""
        with db.session.begin_nested():
            entry = cls(model=cls.model_cls(pid=id_, pure_id=pure_id))
            db.session.add(entry.model)
        return entry

    def commit(self) -> None:
        """Commit."""
        with db.session.begin_nested():
            db.session.merge(self.model)

    def set_state(self, state: str, *, value: bool = True) -> None:
        """Set archived."""
        if state == "imported_in_repo":
            self.model.imported_in_repo = value
        if state == "marked_as_exported":
            self.model.marked_as_exported = value
        db.session.merge(self.model)
