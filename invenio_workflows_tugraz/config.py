# -*- coding: utf-8 -*-
#
# Copyright (C) 2022-2025 Graz University of Technology.
#
# invenio-workflows-tugraz is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Configuration file."""


from invenio_i18n import gettext as _
from invenio_rdm_records.services.pids.providers import ExternalPIDProvider

from .imoox import imoox_import_func
from .openaccess import import_func, openaccess_filter
from .teachcenter import teachcenter_import_func
from .theses import (
    create_func,
    duplicate_func,
    import_from_alma_func,
    import_from_cms_func,
    theses_create_aggregator,
    theses_filter,
    theses_update_aggregator,
    update_func,
)

WORKFLOWS_ALMA_REPOSITORY_RECORDS_IMPORT_FUNC = import_from_alma_func
""""""

WORKFLOWS_ALMA_REPOSITORY_RECORDS_UPDATE_AGGREGATOR = theses_update_aggregator
""""""

WORKFLOWS_ALMA_REPOSITORY_RECORDS_UPDATE_FUNC = update_func
""""""

WORKFLOWS_ALMA_ALMA_RECORDS_CREATE_FUNC = create_func
""""""

WORKFLOWS_ALMA_ALMA_RECORDS_CREATE_AGGREGATOR = theses_create_aggregator
""""""

WORKFLOWS_CAMPUSONLINE_THESES_FILTER = theses_filter()
""""""

WORKFLOWS_CAMPUSONLINE_IMPORT_FUNC = import_from_cms_func
""""""

WORKFLOWS_CAMPUSONLINE_DUPLICATE_FUNC = duplicate_func
""""""

WORKFLOWS_IMOOX_REPOSITORY_IMPORT_FUNC = imoox_import_func
""""""

WORKFLOWS_LOM_PERSISTENT_IDENTIFIER_PROVIDERS = [
    ExternalPIDProvider("moodle", "moodle", label=_("MOODLE ID")),
]
"""List of persistent identifier providers.

The values are added to the LOM_PERSISTENT_IDENTIFIER_PROVIDERS list.
"""

WORKFLOWS_LOM_PERSISTENT_IDENTIFIERS = {
    "moodle": {
        "providers": ["moodle"],
        "required": False,
        "label": _("MOODLE"),
    },
    "moodle_alternative": {
        "providers": ["moodle"],
        "required": False,
        "label": _("MOODLE"),
    },
}
"""Dict of persistent identifiers.

The values are added to the LOM_PERSISTENT_IDENTIFIERS dict.
"""

WORKFLOWS_MOODLE_REPOSITORY_IMPORT_FUNC = teachcenter_import_func
""""""

WORKFLOWS_PURE_IMPORT_FUNC = import_func
"""See corresponding varaible in invenio-pure."""

WORKFLOWS_PURE_FILTER_RECORDS = openaccess_filter()

WORKFLOWS_PURE_MARK_EXPORTED = False
"""It enables to configure if imported records should be marked as exported.

In production this should be enabled but for testing purpose it is practical to
have this flag. it enables the option to import multiple times without changing
the record in pure.
"""
