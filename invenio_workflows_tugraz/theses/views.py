# SPDX-FileCopyrightText: 2022-2026 Graz University of Technology.
# SPDX-License-Identifier: MIT

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
