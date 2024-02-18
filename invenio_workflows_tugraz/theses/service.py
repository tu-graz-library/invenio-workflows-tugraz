# -*- coding: utf-8 -*-
#
# Copyright (C) 2024 Graz University of Technology.
#
# invenio-workflows-tugraz is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Service for theses workflow."""

from flask_principal import Identity
from invenio_records_resources.services.base import Service
from invenio_records_resources.services.uow import RecordCommitOp, unit_of_work

from .api import WorkflowTheses


class WorkflowThesesService(Service):
    """Workflow theses service."""

    @property
    def theses_cls(self) -> WorkflowTheses:
        """Theses cls."""
        return self.config.theses_cls

    @unit_of_work()
    def create(self, _: Identity, id_: str, cms_id: str, uow=None) -> None:
        """Create."""
        print(f"WorkflowThesesService.create id_: {id_}, cms_id: {cms_id}")
        entry = self.theses_cls.create(id_, cms_id)
        uow.register(RecordCommitOp(entry))

    @unit_of_work()
    def set_ready_to(self, _: Identity, id_: str, state: str, uow=None) -> None:
        """Archive."""
        # self.require_permission(identity, state) # noqa: ERA001
        entry = self.theses_cls.get(id_)
        entry.set_ready_to(id_, state=state)
        uow.register(RecordCommitOp(entry))

    def get_ready_to(self, _: Identity, state: str) -> list[tuple[str, str]]:
        """Get archived."""
        # self.require_permission(identity, state) # noqa: ERA001
        return self.theses_cls.get_ready_to(state=state)

    @unit_of_work()
    def set_state(self, _: Identity, id_: str, state: str, uow=None) -> None:
        """Archive."""
        # self.require_permission(identity, state) # noqa: ERA001
        entry = self.theses_cls.get(id_)
        entry.set_state(id_, state=state)
        uow.register(RecordCommitOp(entry))
