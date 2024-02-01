# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
#
# Copyright (C) 2022-2024 Graz University of Technology.
#
# Invenio-Records-Marc21 is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.


"""Blueprint definitions."""

from flask import Blueprint, Flask, g, redirect
from invenio_records_marc21.proxies import current_records_marc21
from werkzeug.wrappers import Response as BaseResponse

from .decorators import pass_record_from_pid


@pass_record_from_pid
def record_from_pid(record: dict, **__: dict) -> BaseResponse:
    """Redirect to record's latest version page."""
    return redirect(record["links"]["self_html"], code=301)


@pass_record_from_pid
def uploads_from_thesesid(record: dict, **__: dict) -> BaseResponse:
    """Upload introduced by theses id."""
    marcid = record["id"]
    current_records_marc21.records_service.edit(g.identity, marcid)
    return redirect(f"/publications/uploads/{marcid}", code=301)


def create_blueprint(_: Flask) -> Blueprint:
    """Register blueprint routes on app."""
    blueprint = Blueprint(
        "invenio_workflows_tugraz_theses",
        __name__,
        url_prefix="/theses",
    )

    blueprint.add_url_rule("/<path:pid_value>", view_func=record_from_pid)
    blueprint.add_url_rule("/<path:pid_value>/uploads", view_func=uploads_from_thesesid)

    return blueprint
