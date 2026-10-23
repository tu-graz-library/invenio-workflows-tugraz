# SPDX-FileCopyrightText: 2024-2026 Graz University of Technology.
# SPDX-License-Identifier: MIT

"""Service for theses workflow."""

from typing import cast

from flask_principal import Identity
from invenio_db.uow import UnitOfWork, unit_of_work
from invenio_records_resources.records.api import Record
from invenio_records_resources.services.base import Service
from invenio_records_resources.services.uow import RecordCommitOp

from .api import WorkflowTheses
from .config import WorkflowThesesServiceConfig


class WorkflowThesesService(Service):
    """Workflow theses service."""

    config: WorkflowThesesServiceConfig

    @property
    def theses_cls(self) -> type[WorkflowTheses]:
        """Theses cls."""
        return self.config.theses_cls

    @unit_of_work()
    def create(
        self,
        _: Identity,
        id_: str,
        cms_id: str,
        uow: UnitOfWork,
    ) -> None:
        """Create."""
        entry = self.theses_cls.create(id_, cms_id)
        uow.register(RecordCommitOp(cast(Record, entry)))

    # @unit_of_work()
    # def set_ready_to(
    #     self,
    #     _: Identity,
    #     id_: str,
    #     state: str,
    #     uow: UnitOfWork,
    # ) -> None:
    #     """Archive."""
    #     entry = self.theses_cls.resolve(id_)
    #     entry.set_ready_to(id_, state=state)
    #     uow.register(RecordCommitOp(cast(Record, entry)))

    def get_ready_to(self, _: Identity, state: str) -> list[WorkflowTheses]:
        """Get archived."""
        return self.theses_cls.get_ready_to(state=state)

    @unit_of_work()
    def set_state(
        self,
        _: Identity,
        id_: str,
        state: str,
        uow: UnitOfWork,
    ) -> None:
        """Archive."""
        entry = self.theses_cls.resolve(id_)
        entry.set_state(state=state)
        uow.register(RecordCommitOp(cast(Record, entry)))
