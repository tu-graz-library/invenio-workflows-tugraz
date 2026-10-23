# SPDX-FileCopyrightText: 2022-2026 Graz University of Technology.
# SPDX-License-Identifier: MIT

"""Package serves as a place for the workflows of the repository of the TU Graz."""

from .ext import InvenioWorkflowsTugraz
from .proxies import current_workflows_tugraz

__version__ = "0.15.2"

__all__ = (
    "InvenioWorkflowsTugraz",
    "__version__",
    "current_workflows_tugraz",
)
