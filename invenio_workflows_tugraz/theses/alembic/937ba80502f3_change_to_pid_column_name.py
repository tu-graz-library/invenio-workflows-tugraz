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
from sqlalchemy_utils import UUIDType

# revision identifiers, used by Alembic.
revision = "937ba80502f3"
down_revision = None
branch_labels = ()
depends_on = "02845ec6893c"


def upgrade() -> None:
    """Upgrade database."""
    op.alter_column(
        "workflows_theses",
        "id",
        new_column_name="pid",
        existing_type=UUIDType(),
        type_=sa.String(255),
    )


def downgrade() -> None:
    """Downgrade database."""
    op.alter_column(
        "workflows_theses",
        "pid",
        new_column_name="id",
        existing_type=sa.String(255),
        type_=sa.UUIDType(),
    )
