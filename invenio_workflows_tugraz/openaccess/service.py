# -*- coding: utf-8 -*-
#
# Copyright (C) 2025-2026 Graz University of Technology.
#
# invenio-workflows-tugraz is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Service for openaccess workflow."""
from typing import cast

from flask_principal import Identity
from invenio_db.uow import UnitOfWork, unit_of_work
from invenio_records_resources.records.api import Record
from invenio_records_resources.services.base import Service
from invenio_records_resources.services.uow import RecordCommitOp

from .api import WorkflowOpenaccess
from .config import WorkflowOpenaccessServiceConfig


class WorkflowOpenaccessService(Service):
    """Workflow openaccess service."""

    config: WorkflowOpenaccessServiceConfig

    @property
    def openaccess_cls(self) -> type[WorkflowOpenaccess]:
        """Theses cls."""
        return self.config.openaccess_cls

    def get_ready_to(self, _: Identity, state: str) -> list[WorkflowOpenaccess]:
        """Get archived."""
        return self.openaccess_cls.get_ready_to(state=state)

    @unit_of_work()
    def create(
        self,
        _: Identity,
        id_: str,
        pure_id: str,
        uow: UnitOfWork,
    ) -> None:
        """Create."""
        entry = self.openaccess_cls.create(id_, pure_id)
        uow.register(RecordCommitOp(cast(Record, entry)))

    @unit_of_work()
    def set_state(
        self,
        _: Identity,
        id_: str,
        state: str,
        uow: UnitOfWork,
        *,
        value: bool = True,
    ) -> None:
        """Archive."""
        entry = self.openaccess_cls.resolve(id_)
        entry.set_state(state=state, value=value)
        uow.register(RecordCommitOp(cast(Record, entry)))
