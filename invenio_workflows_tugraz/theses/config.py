# -*- coding: utf-8 -*-
#
# Copyright (C) 2024 Graz University of Technology.
#
# invenio-workflows-tugraz is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Config for theses workflow."""

from invenio_records_resources.services.base.config import (
    ConfiguratorMixin,
    ServiceConfig,
)

from .api import WorkflowTheses


class WorkflowThesesServiceConfig(ServiceConfig, ConfiguratorMixin):
    """Workflow theses service config."""

    theses_cls = WorkflowTheses
