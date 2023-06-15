# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Graz University of Technology.
#
# invenio-workflows-tugraz is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Pytest configuration.

See https://pytest-invenio.readthedocs.io/ for documentation on which test
fixtures are available.
"""


from collections.abc import Callable

import pytest
from flask import Flask

from invenio_workflows_tugraz import InvenioWorkflowsTugraz


@pytest.fixture(scope="module")
def create_app(instance_path: str) -> Callable:
    """Application factory fixture."""

    def factory(**config: dict) -> Flask:
        app = Flask("testapp", instance_path=instance_path)
        app.config.update(**config)
        InvenioWorkflowsTugraz(app)
        return app

    return factory


@pytest.fixture()
def embargoed_record_xml() -> str:
    """Embargoed record fixture."""
    return """
    <record xmlns="http://www.loc.gov/MARC21/slim">
          <leader>06215nam a2200505 c 4500</leader>
          <datafield ind1="7" ind2=" " tag="971">
            <subfield code="a">gesperrt</subfield>
            <subfield code="b">27.01.2023</subfield>
            <subfield code="c">27.01.2025</subfield>
          </datafield>
    </record>
    """
