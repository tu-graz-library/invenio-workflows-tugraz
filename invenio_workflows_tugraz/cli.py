# -*- coding: utf-8 -*-
#
# Copyright (C) 2024 Graz University of Technology.
#
# invenio-workflows-tugraz is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""CLI for workflows."""

from click import group

from .theses.cli import theses_group


@group()
def workflows() -> None:
    """Workflows cli."""


workflows.add_command(theses_group)
