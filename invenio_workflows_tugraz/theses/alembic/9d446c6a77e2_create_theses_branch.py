# SPDX-FileCopyrightText: 2024-2026 Graz University of Technology.
# SPDX-License-Identifier: MIT

"""Alembic create branch for theses workflow."""

# revision identifiers, used by Alembic.
revision = "9d446c6a77e2"
down_revision = None
branch_labels = ("workflows_theses",)
depends_on = "dbdbc1b19cf2"


def upgrade() -> None:
    """Upgrade database."""


def downgrade() -> None:
    """Downgrade database."""
