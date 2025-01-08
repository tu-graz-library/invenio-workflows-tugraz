# -*- coding: utf-8 -*-
#
# Copyright (C) 2022-2025 Graz University of Technology.
#
# invenio-workflows-tugraz is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Sphinx configuration."""

from invenio_workflows_tugraz import __version__

# Do not warn on external images.
suppress_warnings = ["image.nonlocal_uri"]

# General information about the project.
project = "invenio-workflows-tugraz"
copyright = "2022, Graz University of Technology"
author = "Graz University of Technology"

nitpick_ignore = [
    ("py:class", "collections.abc.Callable"),
    ("py:class", "flask.app.Flask"),
    ("py:class", "flask_principal.Identity"),
    ("py:class", "invenio_alma.services.sru.AlmaSRUService"),
    ("py:class", "invenio_alma.services.rest.AlmaRESTService"),
    ("py:class", "invenio_campusonline.types.CampusOnlineConfigs"),
    ("py:class", "invenio_campusonline.services.services.CampusOnlineRESTService"),
    ("py:class", "invenio_moodle.services.MoodleRESTService"),
    ("py:class", "invenio_pure.types.PureConfigs"),
    ("py:class", "invenio_records_marc21.services.services.Marc21RecordService"),
    ("py:class", "invenio_records_resources.services.records.results.RecordItem"),
    ("py:class", "invenio_pure.services.services.PureRESTService"),
]

# -- General configuration ---------------------------------------------------

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.coverage",
    "sphinx.ext.doctest",
    "sphinx.ext.intersphinx",
    "sphinx.ext.viewcode",
]

templates_path = ["_templates"]
exclude_patterns = []

# The master toctree document.
master_doc = "index"

# The full version, including alpha/beta/rc tags.
release = __version__

# The language for content autogenerated by Sphinx. Refer to documentation
# for a list of supported languages.
#
# This is also used if you do content translation via gettext catalogs.
# Usually you set "language" from the command line for these cases.
language = "en"

# -- Options for HTML output -------------------------------------------------

html_theme = "alabaster"

html_theme_options = {
    "description": "This package serves as a place for the workflows of the repository of the TU Graz.",
    "github_user": "tu-graz-library",
    "github_repo": "invenio-workflows-tugraz",
    "github_button": False,
    "github_banner": True,
    "show_powered_by": False,
    "extra_nav_links": {
        "invenio-workflows-tugraz@GitHub": "https://github.com/tu-graz-library/invenio-workflows-tugraz",
        "invenio-workflows-tugraz@PyPI": "https://pypi.python.org/pypi/invenio-workflows-tugraz/",
    },
}

# Custom sidebar templates, maps document names to template names.
html_sidebars = {
    "**": [
        "about.html",
        "navigation.html",
        "relations.html",
        "searchbox.html",
        "donate.html",
    ]
}
