# -*- coding: utf-8 -*-
#
# Copyright (C) 2022-2025 Graz University of Technology.
#
# invenio-workflows-tugraz is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Pytest configuration.

See https://pytest-invenio.readthedocs.io/ for documentation on which test
fixtures are available.
"""


from collections import namedtuple

import pytest
from _pytest.fixtures import FixtureFunctionMarker
from invenio_app.factory import create_api


@pytest.fixture(scope="module")
def create_app(instance_path: FixtureFunctionMarker) -> None:  # noqa: ARG001
    """Application factory fixture."""
    return create_api


@pytest.fixture
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


@pytest.fixture
def running_app(
    app: FixtureFunctionMarker,
    location: FixtureFunctionMarker,
    cache: FixtureFunctionMarker,
) -> RunningApp:
    """Fixture provides an app with the typically needed db data loaded."""
    return RunningApp(
        app,
        location,
        cache,
    )
