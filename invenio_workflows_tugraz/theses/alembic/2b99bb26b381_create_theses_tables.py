# -*- coding: utf-8 -*-
#
# Copyright (C) 2024 Graz University of Technology.
#
# invenio-workflows-tugraz is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Alembic create tables for theses workflow."""

import sqlalchemy as sa
import sqlalchemy_utils
from alembic import op

# revision identifiers, used by Alembic.
revision = "2b99bb26b381"
down_revision = None
branch_labels = ()
depends_on = "9d446c6a77e2"


def upgrade() -> None:
    """Upgrade database."""
    op.create_table(
        "workflows_theses",
        sa.Column(
            "id",
            sqlalchemy_utils.types.uuid.UUIDType(),
            nullable=False,
        ),
        sa.Column(
            "cms_id",
            sa.Integer(),
            autoincrement=False,
            nullable=False,
        ),
        sa.Column(
            "archived",
            sa.Boolean(),
            default=False,
        ),
        sa.Column(
            "published",
            sa.Boolean(),
            default=False,
        ),
        sa.Column(
            "ready_to_archive",
            sa.Boolean(),
            default=False,
        ),
        sa.Column(
            "ready_to_publish",
            sa.Boolean(),
            default=False,
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_workflows_theses")),
    )


def downgrade() -> None:
    """Downgrade database."""
    op.drop_table("workflows_theses")
