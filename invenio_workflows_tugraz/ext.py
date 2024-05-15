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
            unprefixed_config = k.replace("WORKFLOWS_", "")

            if k.startswith("WORKFLOWS_TUGRAZ_"):
                app.config.setdefault(k, attr)

            if unprefixed_config in app.config:
                match app.config[unprefixed_config]:
                    case list() as container:
                        container.extend(attr)
                    case dict() as container:
                        container.update(attr)
                    case _:
                        app.config[unprefixed_config] = attr

            elif k.startswith("WORKFLOWS_"):
                match attr:
                    case list():
                        app.config.setdefault(unprefixed_config, [])
                        app.config[unprefixed_config].extend(attr)
                    case dict():
                        app.config.setdefault(unprefixed_config, {})
                        app.config[unprefixed_config].update(attr)
                    case _:
                        app.config[unprefixed_config] = attr

    def init_services(self, app: Flask) -> None:
        """Init services."""
        theses_config = WorkflowThesesServiceConfig.build(app)
        self.theses_service = WorkflowThesesService(config=theses_config)
