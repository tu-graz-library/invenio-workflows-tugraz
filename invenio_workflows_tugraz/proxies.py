# -*- coding: utf-8 -*-
#
# Copyright (C) 2024-2026 Graz University of Technology.
#
# invenio-workflows-tugraz is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

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
