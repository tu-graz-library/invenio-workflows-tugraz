# -*- coding: utf-8 -*-
#
# Copyright (C) 2023-2025 Graz University of Technology.
#
# invenio-workflows-tugraz is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Module test theses."""

from io import BytesIO
from json import load
from pathlib import Path
from shutil import copyfileobj
from xml.etree.ElementTree import Element, fromstring, parse

import pytest
from _pytest.fixtures import FixtureFunctionMarker
from decorator import decorator
from flask import Flask
from flask_principal import Identity
from invenio_access.permissions import system_identity
from invenio_campusonline.types import CampusOnlineID, FilePath
from invenio_records_marc21 import Marc21Metadata
from invenio_records_marc21.proxies import current_records_marc21
from invenio_records_resources.services.uow import UnitOfWork

from invenio_workflows_tugraz.proxies import current_workflows_tugraz
from invenio_workflows_tugraz.theses.convert import CampusOnlineToMarc21
from invenio_workflows_tugraz.theses.theses import (
    theses_import_from_cms_func,
    theses_update_func,
)


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


class BaseMockRecordService:
    """Mock RecordsService class."""

    def read_draft(self, id_: str, identity: Identity) -> dict:
        """Mock read_draft."""

    def edit(self, id_: str, identity: Identity) -> None:
        """Mock edit."""

    def update_draft(self, id_: str, identity: Identity, data: dict) -> None:
        """Mock update draft."""

    def publish(self, id_: str, identity: Identity) -> None:
        """Mock publish."""


class BaseMockThesesService:
    """Mock ThesesService class."""

    def set_state(
        self,
        identity: Identity,
        id_: str,
        state: str,
        uow: UnitOfWork = None,
    ) -> None:
        """Mock set state."""

    def create(
        self,
        _: Identity,
        id_: str,
        cms_id: str,
        uow: UnitOfWork = None,
    ) -> None:
        """Create."""


class BaseMockAlmaService:
    """Mock AlmaService class."""

    def get_record(self, cms_id: str, search_key: str) -> list[str]:
        """Get record."""


@pytest.mark.parametrize(
    ("metadata_from_database", "file_access"),
    [
        (
            {
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
                                },
                            },
                        ],
                    },
                },
                "access": {
                    "embargo": {
                        "until": "9999-12-12",
                        "active": True,
                        "reason": None,
                    },
                },
            },
            "restricted",
        ),
        (
            {
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
                                },
                            },
                        ],
                    },
                },
                "access": {
                    "record": "restricted",
                    "files": "restricted",
                },
            },
            "restricted",
        ),
        (
            {
                "metadata": {
                    "leader": "",
                    "fields": {},
                },
                "access": {
                    "embargo": {
                        "until": "9999-12-12",
                        "active": True,
                        "reason": None,
                    },
                },
            },
            "restricted",
        ),
        (
            {
                "metadata": {
                    "leader": "",
                    "fields": {},
                },
                "access": {},
            },
            "public",
        ),
    ],
)
def test_update_func_keep_restricted_file_access(
    app: Flask,
    embargoed_record_xml: str,
    metadata_from_database: dict,
    file_access: bool,
) -> None:
    """Test update func."""

    class MockRecordItem:
        """Mock RecordItem class."""

        @property
        def data(self) -> dict:
            """Mock data."""
            return metadata_from_database

    class MockRecordsService(BaseMockRecordService):
        """Mock RecordsService class."""

        def read_draft(self, *_: tuple, **__: dict) -> dict:
            """Mock read_draft."""
            return MockRecordItem()

        def update_draft(self, data: dict, *_: dict, **__: dict) -> None:
            """Mock update draft."""
            assert data["access"]["record"] == "public"
            assert data["access"]["files"] == file_access

    class MockAlmaService(BaseMockAlmaService):
        """Mock AlmaService class."""

        def get_record(self, *_: tuple, **__: dict) -> list[str]:
            doc = fromstring(embargoed_record_xml)  # noqa: S314
            return [doc]

    backup_records_services = current_records_marc21.records_service

    current_records_marc21.records_service = MockRecordsService()
    current_workflows_tugraz.theses_service = BaseMockThesesService()
    alma_service = MockAlmaService()

    theses_update_func(system_identity, "aiekd-23382", "77777", alma_service)

    current_records_marc21.records_service = backup_records_services


@pytest.mark.parametrize(
    ("metadata_from_alma", "metadata_expected_in_database"),
    [
        (
            """
            <record xmlns="http://www.loc.gov/MARC21/slim">
              <leader>06215nam a2200505 c 4500</leader>
              <controlfield tag="009">AC11111111</controlfield>
              <datafield ind1="1" ind2=" " tag="971">
                <subfield code="a">Mustermann, Max</subfield>
              </datafield>
              <datafield ind1="1" ind2=" " tag="971">
                <subfield code="a">Musterfrau, Maxine</subfield>
              </datafield>
              <datafield ind1="7" ind2=" " tag="971">
                <subfield code="a">gesperrt</subfield>
                <subfield code="b">28.10.2024</subfield>
                <subfield code="c">28.10.2026</subfield>
              </datafield>
            </record>
            """,
            {
                "metadata": {
                    "leader": "06215nam a2200505 c 4500",
                    "fields": {
                        "009": "AC11111111",
                        "971": [
                            {
                                "ind1": "1",
                                "ind2": "_",
                                "subfields": {
                                    "a": ["Mustermann, Max"],
                                },
                            },
                            {
                                "ind1": "1",
                                "ind2": "_",
                                "subfields": {
                                    "a": ["Musterfrau, Maxine"],
                                },
                            },
                            {
                                "ind1": "7",
                                "ind2": "_",
                                "subfields": {
                                    "a": ["gesperrt"],
                                    "b": ["28.10.2024"],
                                    "c": ["28.10.2026"],
                                },
                            },
                        ],
                    },
                },
            },
        ),
    ],
)
def test_update_func_metadata(
    app: Flask,
    metadata_from_alma: str,
    metadata_expected_in_database: dict,
) -> None:
    """Test update func."""

    class MockRecordItem:
        """Mock RecordItem class."""

        @property
        def data(self) -> dict:
            """Mock data."""
            return {
                "metadata": {},
                "access": {},
            }

    class MockRecordsService(BaseMockRecordService):
        """Mock RecordsService class."""

        def read_draft(self, *_: tuple, **__: dict) -> dict:
            """Mock read_draft."""
            return MockRecordItem()

        def update_draft(self, data: dict, *_: dict, **__: dict) -> None:
            """Mock update draft."""
            assert data["metadata"] == metadata_expected_in_database["metadata"]

    class MockAlmaService(BaseMockAlmaService):
        """Mock AlmaService class."""

        def get_record(self, *_: tuple, **__: dict) -> list[str]:
            doc = fromstring(metadata_from_alma)  # noqa: S314
            return [doc]

    backup_records_services = current_records_marc21.records_service

    current_records_marc21.records_service = MockRecordsService()
    current_workflows_tugraz.theses_service = BaseMockThesesService()
    alma_service = MockAlmaService()

    theses_update_func(system_identity, "aiekd-23382", "77777", alma_service)

    current_records_marc21.records_service = backup_records_services


@pytest.mark.parametrize(
    ("campusonline_metadata", "expected_in_database"),
    [
        (
            """
            <?xml version="1.0" encoding="UTF-8"?>
            <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
              <soapenv:Body>
                <getMetadataByThesisIDResponse xmlns="http://www.campusonline.at/thesisservice/basetypes">
                  <thesis>
                    <attr key="SPVON">2023-03-03 01:15:28</attr>
                    <attr key="SPBIS">2025-03-03 01:15:28</attr>
                  </thesis>
                  <errorCode>0</errorCode>
                </getMetadataByThesisIDResponse>
              </soapenv:Body>
            </soapenv:Envelope>
            """,
            {
                "fields": {
                    "007": "cr#|||||||||||",
                    "008": "230501s????####   #####om####|||#|#### c",
                    "040": [
                        {
                            "ind1": "_",
                            "ind2": "_",
                            "subfields": {
                                "a": [
                                    "AT-UBTUG",
                                ],
                                "b": [
                                    "ger",
                                ],
                                "d": [
                                    "AT-UBTUG",
                                ],
                                "e": [
                                    "rda",
                                ],
                            },
                        },
                    ],
                    "044": [
                        {
                            "ind1": "_",
                            "ind2": "_",
                            "subfields": {
                                "c": [
                                    "XA-AT",
                                ],
                            },
                        },
                    ],
                    "264": [
                        {
                            "ind1": "_",
                            "ind2": "1",
                            "subfields": {
                                "a": [
                                    "Graz",
                                ],
                                "c": [
                                    "DATUM",
                                ],
                            },
                        },
                    ],
                    "300": [
                        {
                            "ind1": "_",
                            "ind2": "_",
                            "subfields": {
                                "a": [
                                    "1 Online-Ressource (Seiten)",
                                ],
                                "b": [
                                    "ill",
                                ],
                            },
                        },
                    ],
                    "336": [
                        {
                            "ind1": "_",
                            "ind2": "_",
                            "subfields": {
                                "b": [
                                    "txt",
                                ],
                            },
                        },
                    ],
                    "337": [
                        {
                            "ind1": "_",
                            "ind2": "_",
                            "subfields": {
                                "b": [
                                    "c",
                                ],
                            },
                        },
                    ],
                    "338": [
                        {
                            "ind1": "_",
                            "ind2": "_",
                            "subfields": {
                                "b": [
                                    "cr",
                                ],
                            },
                        },
                    ],
                    "347": [
                        {
                            "ind1": "_",
                            "ind2": "_",
                            "subfields": {
                                "a": [
                                    "Textdatei",
                                ],
                                "b": [
                                    "PDF",
                                ],
                            },
                        },
                    ],
                    "506": [
                        {
                            "ind1": "0",
                            "ind2": "_",
                            "subfields": {
                                "2": [
                                    "star",
                                ],
                                "f": [
                                    "Unrestricted online access",
                                ],
                            },
                        },
                    ],
                    "546": [
                        {
                            "ind1": "_",
                            "ind2": "_",
                            "subfields": {
                                "a": [
                                    "Zusammenfassung in",
                                ],
                            },
                        },
                    ],
                    "655": [
                        {
                            "ind1": "_",
                            "ind2": "7",
                            "subfields": {
                                "0": [
                                    "(DE-588)4113937-9",
                                ],
                                "2": [
                                    "gnd-content",
                                ],
                                "a": [
                                    "Hochschulschrift",
                                ],
                            },
                        },
                    ],
                    "971": [
                        {
                            "ind1": "7",
                            "ind2": "_",
                            "subfields": {
                                "a": ["gesperrt"],
                                "b": ["03.03.2023"],
                                "c": ["03.03.2025"],
                            },
                        },
                    ],
                },
                "leader": "07878nam a2200421 c 4500",
            },
        ),
    ],
)
def test_import_from_cms_func(
    app: Flask,
    campusonline_metadata: str,
    expected_in_database: dict,
    location: FixtureFunctionMarker,
) -> None:
    """Test import from cms func."""

    class MockCampusOnlineService:
        """Mock campusonline service."""

        def get_metadata(self, _: Identity, __: CampusOnlineID) -> Element:
            """Get metadata."""
            root = fromstring(campusonline_metadata.strip())  # noqa: S314
            xpath = "{http://www.campusonline.at/thesisservice/basetypes}thesis"
            return next(root.iter(xpath))

        def download_file(self, _: Identity, cms_id: CampusOnlineID) -> FilePath:
            """Download file."""
            file_path = f"/tmp/{cms_id}.txt"  # noqa: S108
            tmp_file = BytesIO(b"hello world")
            with Path(file_path).open("wb") as fp:
                copyfileobj(tmp_file, fp)
            return file_path

    cms_service = MockCampusOnlineService()

    draft = theses_import_from_cms_func(system_identity, "77777", cms_service)

    assert draft.data["access"] == {
        "embargo": {
            "active": True,
            "reason": None,
            "until": "9999-12-12",
        },
        "record": "restricted",
        "files": "restricted",
        "status": "embargoed",
    }
    assert draft.data["metadata"] == expected_in_database


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
