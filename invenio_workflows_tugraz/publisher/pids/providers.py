# -*- coding: utf-8 -*-
#
# Copyright (C) 2026 Graz University of Technology.
#
# invenio-workflows-tugraz is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Workflow for publisher pids.providers."""

from flask import Flask
from invenio_rdm_records.services.pids.providers.datacite import DataCiteClient
from invenio_records_marc21.records import Marc21Draft, Marc21Record
from invenio_records_marc21.resources.serializers.datacite import (
    Marc21DataCite43JSONSerializer,
)
from invenio_records_marc21.services.pids import Marc21DataCitePIDProvider
from invenio_records_marc21.services.record.metadata import Marc21Metadata


class PublisherDataCitePIDProvider(Marc21DataCitePIDProvider):
    """Publisher datacite pid provider."""

    name = "publ"

    def __init__(self) -> None:
        """Construct."""
        super().__init__(
            "grazpubl",
            client=DataCiteClient("datacite", config_prefix="DATACITE"),  # type: ignore[no-untyped-call]
            pid_type="publ",  # publisher
            serializer=Marc21DataCite43JSONSerializer(),
            label="DOI",
        )

    def generate_id(self, record: Marc21Draft | Marc21Record, **__: dict) -> str | None:
        """Generate an identifier value."""
        metadata = Marc21Metadata(json=record.metadata)
        identifier_field = metadata.get_field("024.7..q", subf_value="tugraz-publisher")
        if identifier_field is None:
            return None

        return identifier_field.get("a")

    @classmethod
    def is_enabled(cls, _: Flask | None = None) -> bool:
        """Determine if verbund is enabled or not."""
        return True

    @classmethod
    def condition(cls, record: Marc21Draft | Marc21Record) -> bool:
        """If the field exists don't remove it, otherwise remove it.

        Intuitive it could be strange, but since required has to be
        set to True, the provider is used every time, but NOT if the
        condition doesn't hold. So if the field exists it stays in
        required_schemes otherwise it is removed.

        This text refers to the behavior of the create and publish
        methods in
        invenio_records_marc21.services.components.pids.PIDsComponent.

        """
        metadata = Marc21Metadata(json=record.metadata)
        return metadata.exists_field(
            "024",
            "7",
            subf_code="q",
            subf_value="tugraz-publisher",
        )
