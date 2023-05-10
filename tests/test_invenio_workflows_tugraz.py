# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Graz University of Technology.
#
# invenio-workflows-tugraz is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Module tests."""

from flask import Flask

from invenio_workflows_tugraz import InvenioWorkflowsTugraz, __version__


def test_version() -> None:
    """Test version import."""
    assert __version__


def test_init() -> None:
    """Test extension initialization."""
    app = Flask("testapp")
    ext = InvenioWorkflowsTugraz(app)
    assert "invenio-workflows-tugraz" in app.extensions

    app = Flask("testapp")
    ext = InvenioWorkflowsTugraz()
    assert "invenio-workflows-tugraz" not in app.extensions
    ext.init_app(app)
    assert "invenio-workflows-tugraz" in app.extensions
