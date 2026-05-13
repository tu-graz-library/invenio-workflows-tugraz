# -*- coding: utf-8 -*-
#
# Copyright (C) 2026 Graz University of Technology.
#
# invenio-workflows-tugraz is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Thesis migration for cms id."""

from click import secho
from invenio_records_marc21.records import Marc21Draft, Marc21Record

from invenio_workflows_tugraz.theses.migration.tasks import update_pids


def execute_upgrade() -> None:
    """Execute upgrade."""
    apis = [Marc21Record, Marc21Draft]

    for api_cls in apis:
        counter = 0
        for record_metadata in api_cls.model_cls.query.all():
            record = api_cls(record_metadata.data, model=record_metadata)
            update_pids.delay(str(record.id))
            counter += 1

        secho(f"update pids {counter} send to celery", fg="green")


if __name__ == "__main__":
    execute_upgrade()
