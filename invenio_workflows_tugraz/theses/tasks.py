# -*- coding: utf-8 -*-
#
# Copyright (C) 2024 Graz University of Technology.
#
# invenio-workflows-tugraz is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Tasks for theses workflow."""

from datetime import datetime, timezone

from celery import shared_task
from flask import current_app
from invenio_campusonline.api import set_status
from invenio_campusonline.utils import config_variables

from ..proxies import current_workflows_tugraz


@shared_task(ignore_result=True)
def status_arch() -> None:
    """Set status to ARCH (archived)."""
    configs = config_variables(current_app)
    today = datetime.now(tz=timezone.utc).strftime("%Y-%m-%d")

    service = current_workflows_tugraz.theses_service
    cms_ids = service.get_ready_to(state="archive")

    for id_, cms_id in cms_ids:
        set_status(configs.endpoint, configs.token, cms_id, "ARCH", today)
        service.set_state(id_, state="archived")
        current_app.logger.info("Theses %s has been imported successfully.", cms_id)


@shared_task(ignore_result=True)
def status_pub() -> None:
    """Set status to PUB (published)."""
    configs = config_variables(current_app)
    today = datetime.now(tz=timezone.utc).strftime("%Y-%m-%d")

    service = current_workflows_tugraz.theses_service
    cms_ids = service.get_ready_to(state="publish")

    for id_, cms_id in cms_ids:
        set_status(configs.endpoint, configs.token, cms_id, "PUB", today)
        service.set_state(id_, state="published")
        current_app.logger.info("Theses %s has been updated successfully.", cms_id)
