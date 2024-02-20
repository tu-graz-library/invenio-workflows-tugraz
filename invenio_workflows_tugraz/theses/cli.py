# -*- coding: utf-8 -*-
#
# Copyright (C) 2024 Graz University of Technology.
#
# invenio-workflows-tugraz is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""CLI for theses workflow."""


from click import group, secho
from flask.cli import with_appcontext
from invenio_access.permissions import system_identity

from ..proxies import current_workflows_tugraz
from ..types import Color


@group("theses")
def theses_group() -> None:
    """Theses group."""


@theses_group.command()
@with_appcontext
def ready_to_archive() -> None:
    """Ready to archive."""
    theses_service = current_workflows_tugraz.theses_service
    entries = theses_service.get_ready_to(system_identity, state="archive_in_cms")
    secho("ready to archive in cms", fg=Color.neutral)
    for entry in entries:
        secho(f"pid: {entry.pid}, cms_id: {entry.cms_id}", fg=Color.neutral)


@theses_group.command()
@with_appcontext
def ready_to_publish() -> None:
    """Ready to archive."""
    theses_service = current_workflows_tugraz.theses_service
    entries = theses_service.get_ready_to(system_identity, state="publish_in_cms")
    secho("ready to publish in cms", fg=Color.neutral)
    for entry in entries:
        secho(f"pid: {entry.pid}, cms_id: {entry.cms_id}", fg=Color.neutral)
