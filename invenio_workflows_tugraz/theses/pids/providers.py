# -*- coding: utf-8 -*-
#
# Copyright (C) 2026 Graz University of Technology.
#
# invenio-workflows-tugraz is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Theses Workflows pids.providers."""

from flask import Flask
from invenio_rdm_records.services.pids.providers import PIDProvider
from invenio_records_marc21.records import Marc21Draft, Marc21Record
from invenio_records_marc21.services.record.metadata import Marc21Metadata


class CMSPIDProvider(PIDProvider):
    """Campusonline (CMS) id PID Provider."""

    name = "cms"

    def __init__(self) -> None:
        """Construct."""
        super().__init__(
            "cms",
            pid_type="cms",
            label="CMS ID",
        )

    def generate_id(self, record: Marc21Draft | Marc21Record, **__: dict) -> str:
        """Generate an identifier value."""
        metadata = Marc21Metadata(json=record.metadata)
        return metadata.get_field("995...a")["subfields"]["a"][0]

    @classmethod
    def is_enabled(cls, _: Flask) -> bool:
        """Determine if verbund is enabled or not."""
        return True
