# -*- coding: utf-8 -*-
#
# Copyright (C) 2025 Graz University of Technology.
#
# invenio-workflows-tugraz is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

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
