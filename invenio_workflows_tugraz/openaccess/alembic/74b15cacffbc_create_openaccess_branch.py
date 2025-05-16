# -*- coding: utf-8 -*-
#
# Copyright (C) 2025 Graz University of Technology.
#
# invenio-workflows-tugraz is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

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
