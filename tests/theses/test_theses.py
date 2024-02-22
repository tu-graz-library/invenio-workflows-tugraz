# -*- coding: utf-8 -*-
#
# Copyright (C) 2023-2024 Graz University of Technology.
#
# invenio-workflows-tugraz is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Module test theses."""

from xml.etree.ElementTree import fromstring

from flask import Flask
from flask_principal import Identity
from invenio_access.permissions import system_identity
from invenio_records_marc21.proxies import current_records_marc21
from invenio_records_resources.services.uow import UnitOfWork

from invenio_workflows_tugraz.proxies import current_workflows_tugraz
from invenio_workflows_tugraz.theses.theses import update_func


def test_update_func(
    running_app: Flask,  # noqa: ARG001
    embargoed_record_xml: str,
) -> None:
    """Test update func."""

    class MockRecordItem:
        """Mock RecordItem class."""

        @property
        def data(self) -> dict:
            """Mock data."""
            return {
                "metadata": {
                    "leader": "",
                    "fields": {
                        "971": [
                            {
                                "ind1": "7",
                                "ind2": " ",
                                "subfields": {
                                    "a": [
                                        "gesperrt",
                                    ],
                                    "b": [
                                        "27.01.2023",
                                    ],
                                    "c": [
                                        "27.01.2025",
                                    ],
                                },
                            },
                        ],
                    },
                },
                "access": {
                    "record": "restricted",
                    "files": "restricted",
                },
            }

    class MockRecordsService:
        """Mock RecordsService class."""

        def read_draft(self, id_: str, identity: Identity) -> dict:  # noqa: ARG002
            """Mock read_draft."""
            return MockRecordItem()

        def edit(self, id_: str, identity: Identity) -> None:
            """Mock edit."""

        def update_draft(
            self,
            id_: str,  # noqa: ARG002
            identity: Identity,  # noqa: ARG002
            data: dict,
        ) -> None:
            """Mock update draft."""
            assert data["access"]["record"] == "public"
            assert data["access"]["files"] == "restricted"

        def publish(self, id_: str, identity: Identity) -> None:
            """Mock publish."""

    class MockAlmaService:
        """Mock AlmaService class."""

        def get_record(self, cms_id: str, search_key: str) -> list[str]:  # noqa: ARG002
            doc = fromstring(embargoed_record_xml)  # noqa: S314
            return [doc]

    class MockThesesService:
        """Mock ThesesService class."""

        def set_state(
            self,
            identity: Identity,
            id_: str,
            state: str,
            uow: UnitOfWork = None,
        ) -> None:
            """Mock set state."""

    current_records_marc21.records_service = MockRecordsService()
    current_workflows_tugraz.theses_service = MockThesesService()
    alma_service = MockAlmaService()

    update_func(system_identity, "aiekd-23382", "77777", alma_service)
