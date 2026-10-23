# SPDX-FileCopyrightText: 2025-2026 Graz University of Technology.
# SPDX-License-Identifier: MIT

"""Alembic create tables for openaccess workflow."""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "bf15edb5b389"
down_revision = None
branch_labels = ()
depends_on = "74b15cacffbc"


def upgrade() -> None:
    """Upgrade database."""
    op.create_table(
        "workflows_openaccess",
        sa.Column("created", sa.DateTime(), nullable=False),
        sa.Column("updated", sa.DateTime(), nullable=False),
        sa.Column(
            "pid",
            sa.String(255),
            nullable=False,
        ),
        sa.Column(
            "pure_id",
            sa.String(255),
            nullable=False,
        ),
        sa.Column(
            "imported_in_repo",
            sa.Boolean(),
            default=False,
        ),
        sa.Column(
            "marked_as_exported",
            sa.Boolean(),
            default=False,
        ),
        sa.PrimaryKeyConstraint("pid", name=op.f("pk_workflows_openaccess")),
    )


def downgrade() -> None:
    """Downgrade database."""
    op.drop_table("workflows_openaccess")
