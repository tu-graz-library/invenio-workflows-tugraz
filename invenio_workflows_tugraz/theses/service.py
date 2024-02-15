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

from .api import WorkflowTheses


class WorkflowThesesService(Service):
    """Workflow theses service."""

    @property
    def theses_cls(self) -> WorkflowTheses:
        """Theses cls."""
        return self.config.theses_cls

    def create(self, _: Identity, id_: str, cms_id: str) -> None:
        """Create."""
        self.theses_cls.create(id_, cms_id)

    def set_ready_to(self, _: Identity, id_: str, state: str) -> None:
        """Archive."""
        # self.require_permission(identity, state) # noqa: ERA001
        self.theses_cls.set_ready_to(id_, state=state)

    def get_ready_to(self, _: Identity, state: str) -> list[tuple[str, str]]:
        """Get archived."""
        # self.require_permission(identity, state) # noqa: ERA001
        return self.theses_cls.get_ready_to(state=state)

    def set_state(self, _: Identity, id_: str, state: str) -> None:
        """Archive."""
        # self.require_permission(identity, state) # noqa: ERA001
        self.theses_cls.set_state(id_, state=state)
