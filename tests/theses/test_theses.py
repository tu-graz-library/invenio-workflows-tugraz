# -*- coding: utf-8 -*-
#
# Copyright (C) 2023-2025 Graz University of Technology.
#
# invenio-workflows-tugraz is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Module test theses."""

from json import load
from pathlib import Path
from xml.etree.ElementTree import fromstring, parse

import pytest
from decorator import decorator
from flask import Flask
from flask_principal import Identity
from invenio_access.permissions import system_identity
from invenio_records_marc21 import Marc21Metadata
from invenio_records_marc21.proxies import current_records_marc21
from invenio_records_resources.services.uow import UnitOfWork

from invenio_workflows_tugraz.proxies import current_workflows_tugraz
from invenio_workflows_tugraz.theses.convert import CampusOnlineToMarc21
from invenio_workflows_tugraz.theses.theses import theses_update_func


def load_as_json(func: callable) -> any:
    """Decorat to load content of file as dictionary from a json file."""

    def wrapper(*args: dict, **__: dict) -> any:
        parent = Path(__file__).parent
        tree = parse(Path(f"{parent}/data/{args[1]}.xml"))  # noqa: S314
        xpath = "{http://www.campusonline.at/thesisservice/basetypes}thesis"
        test = next(tree.getroot().iter(xpath))

        with Path(f"{parent}/data/{args[2]}.json").open() as fp:
            expected = load(fp)
        return func(test, expected)

    return decorator(wrapper, func)


def test_update_func(
    app: Flask,  # noqa: ARG001
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

    theses_update_func(system_identity, "aiekd-23382", "77777", alma_service)


@pytest.mark.parametrize(
    ("test", "expected"),
    [("empty_test", "empty_expected")],
)
@load_as_json
def test_convert(test: dict, expected: dict) -> None:
    """Test theses convert."""
    record = Marc21Metadata()
    visitor = CampusOnlineToMarc21(record)

    visitor.visit(test, record)

    assert record.json == expected
