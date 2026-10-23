# SPDX-FileCopyrightText: 2024-2026 Graz University of Technology.
# SPDX-License-Identifier: MIT

"""CLI for workflows."""

from click import group

from .migration_diglib_repository.cli import migration_group
from .theses.cli import theses_group


@group()
def workflows() -> None:
    """Workflows cli."""


workflows.add_command(theses_group)
workflows.add_command(migration_group)
