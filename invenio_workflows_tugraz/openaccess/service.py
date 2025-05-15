# -*- coding: utf-8 -*-
#
# Copyright (C) 2025 Graz University of Technology.
#
# invenio-workflows-tugraz is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Service for openaccess workflow."""

from flask_principal import Identity
from invenio_records_resources.services.base import Service
from invenio_records_resources.services.uow import (
    RecordCommitOp,
    UnitOfWork,
    unit_of_work,
)

from .api import WorkflowOpenaccess


class WorkflowOpenaccessService(Service):
    """Workflow openaccess service."""

    @property
    def openaccess_cls(self) -> WorkflowOpenaccess:
        """Theses cls."""
        return self.config.openaccess_cls

    def get_ready_to(self, _: Identity, state: str) -> list[tuple[str, str]]:
        """Get archived."""
        return self.openaccess_cls.get_ready_to(state=state)

    @unit_of_work()
    def create(
        self,
        _: Identity,
        id_: str,
        pure_id: str,
        uow: UnitOfWork = None,
    ) -> None:
        """Create."""
        entry = self.openaccess_cls.create(id_, pure_id)
        uow.register(RecordCommitOp(entry))

    @unit_of_work()
    def set_state(
        self,
        _: Identity,
        id_: str,
        state: str,
        uow: UnitOfWork = None,
        *,
        value: bool = True,
    ) -> None:
        """Archive."""
        entry = self.openaccess_cls.resolve(id_)
        entry.set_state(state=state, value=value)
        uow.register(RecordCommitOp(entry))
