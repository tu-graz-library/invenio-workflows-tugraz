# SPDX-FileCopyrightText: 2026 Graz University of Technology.
# SPDX-License-Identifier: MIT

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

    def generate_id(self, record: Marc21Draft | Marc21Record, **__: dict) -> str:  # type: ignore[override]
        """Generate an identifier value."""
        metadata = Marc21Metadata(json=record.metadata)
        datafield = metadata.get_field("995...a")
        if datafield is None:
            msg = "no 995 field found to generate an id."
            raise RuntimeError(msg)
        return datafield.get("a")

    @classmethod
    def is_enabled(cls, _: Flask | None) -> bool:
        """Determine if verbund is enabled or not."""
        return True


class VerbundPIDProvider(PIDProvider):
    """Verbund id PID Provider."""

    name = "verbund"

    def __init__(self) -> None:
        """Construct."""
        super().__init__(
            "verbund",
            pid_type="ac",
            label="Verbund ID",
        )

    def generate_id(self, record: Marc21Draft | Marc21Record, **__: dict) -> str:  # type: ignore[override]
        """Generate an identifier value."""
        metadata = Marc21Metadata(json=record.metadata)
        return metadata.get_value("009")

    @classmethod
    def is_enabled(cls, _: Flask | None) -> bool:
        """Determine if verbund is enabled or not."""
        return True
