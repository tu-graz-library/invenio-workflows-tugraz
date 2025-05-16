# -*- coding: utf-8 -*-
#
# Copyright (C) 2022-2025 Graz University of Technology.
#
# invenio-workflows-tugraz is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Open Access Workflows config."""

from invenio_records_resources.services.base.config import (
    ConfiguratorMixin,
    ServiceConfig,
)

from .api import WorkflowOpenaccess


class WorkflowOpenaccessServiceConfig(ServiceConfig, ConfiguratorMixin):
    """Workflow openaccess service config."""

    openaccess_cls = WorkflowOpenaccess
