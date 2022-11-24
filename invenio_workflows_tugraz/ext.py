# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Graz University of Technology.
#
# invenio-workflows-tugraz is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""This package serves as a place for the workflows of the repository of the TU Graz."""

from . import config


class InvenioWorkflowsTugraz:
    """invenio-workflows-tugraz extension."""

    def __init__(self, app=None):
        """Extension initialization."""
        if app:
            self.init_app(app)

    def init_app(self, app):
        """Flask application initialization."""
        self.init_config(app)
        app.extensions["invenio-workflows-tugraz"] = self

    def init_config(self, app):
        """Initialize configuration."""
        app.config.setdefault("ALMA_REPOSITORY_RECORDS_UPDATE_AGGREGATORS", [])
        app.config.setdefault("ALMA_ALMA_RECORDS_CREATE_AGGREGATORS", [])
        app.config.setdefault("CAMPUSONLINE_THESES_FILTERS", [])

        for k in dir(config):
            if k == "WORKFLOW_ALMA_REPOSITORY_RECORDS_UPDATE_AGGREGATORS":
                app.config["ALMA_REPOSITORY_RECORDS_UPDATE_AGGREGATORS"] += getattr(
                    config, k
                )

            elif k == "WORKFLOW_ALMA_ALMA_RECORDS_CREATE_AGGREGATORS":
                app.config["ALMA_ALMA_RECORDS_CREATE_AGGREGATORS"] += getattr(config, k)

            elif k == "WORKFLOW_CAMPUSONLINE_THESES_FILTERS":
                app.config["CAMPUSONLINE_THESES_FILTERS"] += getattr(config, k)

            elif k == "WORKFLOW_CAMPUSONLINE_IMPORT_FUNC":
                app.config["CAMPUSONLINE_IMPORT_FUNC"] = getattr(config, k)

            elif k.startswith("WORKFLOWS_TUGRAZ_"):
                app.config.setdefault(k, getattr(config, k))
