# -*- coding: utf-8 -*-
#
# Copyright (C) 2024 Graz University of Technology.
#
# invenio-workflows-tugraz is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Alembic create tables for theses workflow."""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "eca8ae6a6bc1"
down_revision = None
branch_labels = ()
depends_on = "02845ec6893c"


def upgrade() -> None:
    """Upgrade database."""
    op.add_column(
        "workflows_theses",
        sa.Column("imported_in_repo", sa.Boolean(), default=False),
    )
    op.add_column(
        "workflows_theses",
        sa.Column("updated_in_repo", sa.Boolean(), default=False),
    )
    op.drop_column("workflows_theses", "ready_to_archive_in_cms")
    op.drop_column("workflows_theses", "ready_to_create_in_alma")
    op.drop_column("workflows_theses", "ready_to_update_in_repo")
    op.drop_column("workflows_theses", "ready_to_publish_in_cms")


def downgrade() -> None:
    """Downgrade database."""
    op.add_column(
        "workflows_theses",
        sa.Column("ready_to_archive_in_cms", sa.Boolean(), default=False),
    )
    op.add_column(
        "workflows_theses",
        sa.Column("ready_to_create_in_alma", sa.Boolean(), default=False),
    )
    op.add_column(
        "workflows_theses",
        sa.Column("ready_to_update_in_repo", sa.Boolean(), default=False),
    )
    op.add_column(
        "workflows_theses",
        sa.Column("ready_to_publish_in_cms", sa.Boolean(), default=False),
    )
    op.drop_column("workflows_theses", "imported_in_repo")
    op.drop_column("workflows_theses", "updated_in_repo")
