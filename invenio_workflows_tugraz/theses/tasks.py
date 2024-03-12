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
from invenio_access.permissions import system_identity
from invenio_campusonline import current_campusonline

from ..proxies import current_workflows_tugraz


@shared_task(ignore_result=True)
def status_arch() -> None:
    """Set status to ARCH (archived)."""
    today = datetime.now(tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%S")

    theses_service = current_workflows_tugraz.theses_service
    cms_service = current_campusonline.campusonline_rest_service

    entries = theses_service.get_ready_to(system_identity, state="archive_in_cms")

    for entry in entries:
        cms_id = entry.cms_id
        pid = entry.pid

        try:
            cms_service.set_status(system_identity, cms_id, "ARCH", today)
            theses_service.set_state(system_identity, pid, state="archived_in_cms")

            msg = "Theses %s has been archived successfully."
            current_app.logger.info(msg, cms_id)
        except RuntimeError as e:
            msg = "Theses %s have been produced error %s on archiving."
            current_app.logger.error(msg, cms_id, str(e))


@shared_task(ignore_result=True)
def status_pub() -> None:
    """Set status to PUB (published)."""
    today = datetime.now(tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%S")

    theses_service = current_workflows_tugraz.theses_service
    cms_service = current_campusonline.campusonline_rest_service
    entries = theses_service.get_ready_to(system_identity, state="publish_in_cms")

    for entry in entries:
        cms_id = entry.cms_id
        pid = entry.pid

        try:
            cms_service.set_status(system_identity, cms_id, "PUB", today)
            theses_service.set_state(system_identity, pid, state="published_in_cms")

            msg = "Theses %s has been published successfully."
            current_app.logger.info(msg, cms_id)
        except RuntimeError as e:
            msg = "Theses %s have been produced error %s on publishing."
            current_app.logger.error(msg, cms_id, str(e))
