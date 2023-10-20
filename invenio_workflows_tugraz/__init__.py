# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Graz University of Technology.
#
# invenio-workflows-tugraz is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Package serves as a place for the workflows of the repository of the TU Graz."""

from .ext import InvenioWorkflowsTugraz

__version__ = "0.2.4"

__all__ = ("__version__", "InvenioWorkflowsTugraz")
