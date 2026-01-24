# -*- coding: utf-8 -*-
#
# Copyright (C) 2025-2026 Graz University of Technology.
#
# invenio-workflows-tugraz is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Alembic create tables for openaccess workflow."""


from invenio_db.utils import (
    update_table_columns_column_type_to_datetime,
    update_table_columns_column_type_to_utc_datetime,
)

# revision identifiers, used by Alembic.
revision = "4c136b376379"
down_revision = "bf15edb5b389"
branch_labels = ()
depends_on = None


def upgrade() -> None:
    """Upgrade database."""
    for table_name in ["workflows_openaccess"]:
        update_table_columns_column_type_to_utc_datetime(table_name, "created")
        update_table_columns_column_type_to_utc_datetime(table_name, "updated")


def downgrade() -> None:
    """Downgrade database."""
    for table_name in ["workflows_openaccess"]:
        update_table_columns_column_type_to_datetime(table_name, "created")
        update_table_columns_column_type_to_datetime(table_name, "updated")
