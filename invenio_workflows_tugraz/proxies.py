# SPDX-FileCopyrightText: 2024-2026 Graz University of Technology.
# SPDX-License-Identifier: MIT

"""Proxies."""

from typing import TYPE_CHECKING, cast

from flask import current_app
from werkzeug.local import LocalProxy

if TYPE_CHECKING:
    from .ext import InvenioWorkflowsTugraz

current_workflows_tugraz: InvenioWorkflowsTugraz = cast(
    "InvenioWorkflowsTugraz",
    LocalProxy(lambda: current_app.extensions["invenio-workflows-tugraz"]),
)
"""Helper proxy to get the current workflows tugraz extension."""
