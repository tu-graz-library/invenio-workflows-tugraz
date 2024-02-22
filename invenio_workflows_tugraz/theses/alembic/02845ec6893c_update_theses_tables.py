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
revision = "02845ec6893c"
down_revision = None
branch_labels = ()
depends_on = "2b99bb26b381"


def upgrade() -> None:
    """Upgrade database."""
    op.add_column(
        "workflows_theses",
        sa.Column("archived_in_cms", sa.Boolean(), default=False),
    )
    op.add_column(
        "workflows_theses",
        sa.Column("created_in_alma", sa.Boolean(), default=False),
    )
    op.add_column(
        "workflows_theses",
        sa.Column("published_in_cms", sa.Boolean(), default=False),
    )
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
    op.drop_column("workflows_theses", "archived")
    op.drop_column("workflows_theses", "published")
    op.drop_column("workflows_theses", "ready_to_archive")
    op.drop_column("workflows_theses", "ready_to_publish")


def downgrade() -> None:
    """Downgrade database."""
    op.drop_column("workflows_theses", "archived_in_cms")
    op.drop_column("workflows_theses", "created_in_alma")
    op.drop_column("workflows_theses", "published_in_cms")
    op.drop_column("workflows_theses", "ready_to_archive_in_cms")
    op.drop_column("workflows_theses", "ready_to_create_in_alma")
    op.drop_column("workflows_theses", "ready_to_update_in_repo")
    op.drop_column("workflows_theses", "ready_to_publish_in_cms")

    op.add_column(
        "workflows_theses",
        sa.Column("archived", sa.Boolean(), default=False),
    )
    op.add_column(
        "workflows_theses",
        sa.Column("published", sa.Boolean(), default=False),
    )
    op.add_column(
        "workflows_theses",
        sa.Column("ready_to_archive", sa.Boolean(), default=False),
    )
    op.add_column(
        "workflows_theses",
        sa.Column("ready_to_publish", sa.Boolean(), default=False),
    )
