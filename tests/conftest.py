# -*- coding: utf-8 -*-
#
# Copyright (C) 2022-2024 Graz University of Technology.
#
# invenio-workflows-tugraz is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Pytest configuration.

See https://pytest-invenio.readthedocs.io/ for documentation on which test
fixtures are available.
"""


from collections import namedtuple
from collections.abc import Callable

import pytest
from flask import Flask
from invenio_db import InvenioDB
from invenio_records_marc21 import InvenioRecordsMARC21
from invenio_search import InvenioSearch

from invenio_workflows_tugraz import InvenioWorkflowsTugraz


@pytest.fixture(scope="module")
def create_app(instance_path: str) -> Callable:
    """Application factory fixture."""

    def factory(**config: dict) -> Flask:
        app = Flask("testapp", instance_path=instance_path)
        app.config.update(**config)
        InvenioWorkflowsTugraz(app)
        InvenioSearch(app)
        InvenioDB(app)
        InvenioRecordsMARC21(app)
        return app

    return factory


@pytest.fixture()
def embargoed_record_xml() -> str:
    """Embargoed record fixture."""
    return """
    <record xmlns="http://www.loc.gov/MARC21/slim">
          <leader>06215nam a2200505 c 4500</leader>
          <controlfield tag="009">AC11111111</controlfield>
          <datafield ind1="7" ind2=" " tag="971">
            <subfield code="a">gesperrt</subfield>
            <subfield code="b">27.01.2023</subfield>
            <subfield code="c">27.01.2025</subfield>
          </datafield>
    </record>
    """


RunningApp = namedtuple(  # noqa: PYI024
    "RunningApp",
    [
        "app",
        "location",
        "cache",
    ],
)


@pytest.fixture()
def running_app(
    app,  # noqa: ANN001
    location,  # noqa: ANN001
    cache,  # noqa: ANN001
) -> RunningApp:
    """Fixture provides an app with the typically needed db data loaded."""
    return RunningApp(
        app,
        location,
        cache,
    )
