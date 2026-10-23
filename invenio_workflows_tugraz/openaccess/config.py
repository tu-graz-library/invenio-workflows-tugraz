# SPDX-FileCopyrightText: 2022-2026 Graz University of Technology.
# SPDX-License-Identifier: MIT

"""Open Access Workflows config."""

from typing import ClassVar

from invenio_records_resources.services.base.config import (
    ConfiguratorMixin,
    ServiceConfig,
)

from .api import WorkflowOpenaccess


class WorkflowOpenaccessServiceConfig(ServiceConfig, ConfiguratorMixin):
    """Workflow openaccess service config."""

    openaccess_cls: ClassVar[type[WorkflowOpenaccess]] = WorkflowOpenaccess
