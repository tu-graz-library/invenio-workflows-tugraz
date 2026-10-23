# SPDX-FileCopyrightText: 2024-2026 Graz University of Technology.
# SPDX-License-Identifier: MIT

"""Config for theses workflow."""

from invenio_records_resources.services.base.config import (
    ConfiguratorMixin,
    ServiceConfig,
)

from .api import WorkflowTheses


class WorkflowThesesServiceConfig(ServiceConfig, ConfiguratorMixin):
    """Workflow theses service config."""

    theses_cls = WorkflowTheses
