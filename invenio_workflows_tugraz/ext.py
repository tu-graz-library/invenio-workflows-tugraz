# -*- coding: utf-8 -*-
#
# Copyright (C) 2022-2024 Graz University of Technology.
#
# invenio-workflows-tugraz is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Initialize the package."""

from flask import Flask

from . import config
from .theses import WorkflowThesesService, WorkflowThesesServiceConfig


class InvenioWorkflowsTugraz:
    """invenio-workflows-tugraz extension."""

    def __init__(self, app: Flask = None) -> None:
        """Extension initialization."""
        if app:
            self.init_app(app)

    def init_app(self, app: Flask) -> None:
        """Flask application initialization."""
        self.init_config(app)
        self.init_services(app)
        app.extensions["invenio-workflows-tugraz"] = self

    def init_config(self, app: Flask) -> None:
        """Initialize configuration."""
        for k in dir(config):
            attr = getattr(config, k)

            if k == "WORKFLOW_ALMA_REPOSITORY_RECORDS_UPDATE_AGGREGATOR":
                app.config["ALMA_REPOSITORY_RECORDS_UPDATE_AGGREGATOR"] = attr

            elif k == "WORKFLOW_ALMA_REPOSITORY_RECORDS_UPDATE_FUNC":
                app.config["ALMA_REPOSITORY_RECORDS_UPDATE_FUNC"] = attr

            elif k == "WORKFLOW_ALMA_ALMA_RECORDS_CREATE_AGGREGATOR":
                app.config["ALMA_ALMA_RECORDS_CREATE_AGGREGATOR"] = attr

            elif k == "WORKFLOW_ALMA_ALMA_RECORDS_CREATE_FUNC":
                app.config["ALMA_ALMA_RECORDS_CREATE_FUNC"] = attr

            elif k == "WORKFLOW_CAMPUSONLINE_THESES_FILTER":
                app.config["CAMPUSONLINE_THESES_FILTER"] = attr

            elif k == "WORKFLOW_CAMPUSONLINE_IMPORT_FUNC":
                app.config["CAMPUSONLINE_IMPORT_FUNC"] = attr

            elif k == "WORKFLOW_CAMPUSONLINE_DUPLICATE_FUNC":
                app.config["CAMPUSONLINE_DUPLICATE_FUNC"] = attr

            elif k.startswith("WORKFLOWS_TUGRAZ_"):
                app.config.setdefault(k, attr)

    def init_services(self, app: Flask) -> None:
        """Init services."""
        theses_config = WorkflowThesesServiceConfig.build(app)
        self.theses_service = WorkflowThesesService(config=theses_config)
