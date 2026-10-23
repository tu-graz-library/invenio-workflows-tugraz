# SPDX-FileCopyrightText: 2025-2026 Graz University of Technology.
# SPDX-License-Identifier: MIT

"""Alembic create branch for openaccess workflow."""

# revision identifiers, used by Alembic.
revision = "74b15cacffbc"
down_revision = None
branch_labels = ("workflows_openaccess",)
depends_on = "dbdbc1b19cf2"


def upgrade() -> None:
    """Upgrade database."""


def downgrade() -> None:
    """Downgrade database."""
