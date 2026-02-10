# -*- coding: utf-8 -*-
#
# Copyright (C) 2025-2026 Graz University of Technology.
#
# invenio-workflows-tugraz is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Convert csv to marc21."""

from invenio_records_marc21.services.record.metadata import Marc21Metadata


class CSVToMarc21:
    """CSVToMarc21."""

    def __init__(self, record: Marc21Metadata) -> None:
        """Construct."""
        self.filename: str = ""

        record.emplace_leader("07878nam a2200421 c 4500")
        record.emplace_controlfield("007", "cr#|||||||||||")
        record.emplace_controlfield("008", "230501s????####   #####om####|||#|#### c")
        record.emplace_datafield(
            "040...",
            subfs={"a": "AT-UBTUG", "b": "ger", "d": "AT-UBTUG", "e": "rda"},
        )
        record.emplace_datafield("044...", subfs={"c": "XA-AT"})
        record.emplace_datafield("264..1.", subfs={"a": "Graz", "c": "DATUM"})
        record.emplace_datafield(
            "300...",
            subfs={"a": "1 Online-Ressource (Seiten)", "b": "ill"},
        )
        record.emplace_datafield("336...", subfs={"b": "txt"})
        record.emplace_datafield("337...", subfs={"b": "c"})
        record.emplace_datafield("338...", subfs={"b": "cr"})
        record.emplace_datafield("347...", subfs={"a": "Textdatei", "b": "PDF"})
        record.emplace_datafield(
            "506.0..",
            subfs={"2": "star", "f": "Unrestricted online access"},
        )
        record.emplace_datafield("546...", subfs={"a": "Zusammenfassung in"})
        record.emplace_datafield(
            "655..7.",
            subfs={
                "a": "Hochschulschrift",
                "0": "(DE-588)4113937-9",
                "2": "gnd-content",
            },
        )
        record.emplace_datafield(
            "710.2..",
            subfs={
                "a": "Technische Universität Graz.",
                "0": "(DE-588)2042894-7",
                "4": "dgg",
            },
        )

    def convert(self, row: dict, record: Marc21Metadata) -> None:
        """Convert."""
        for key, value in row.items():
            self.visit_column(key, value, record)

    def visit_column(self, key: str, value: str, record: Marc21Metadata) -> None:
        """Run column function."""

        def func_not_found(_: str, __: Marc21Metadata) -> None:
            msg = f"NO visitor node: '{key}'"
            raise ValueError(msg)

        visit_func = getattr(self, f"visit_{key}", func_not_found)
        visit_func(value, record)

    def visit_id(self, value: str, record: Marc21Metadata) -> None:
        """Visit ."""
        # add to 500 field

    def visit_doi(self, value: str, record: Marc21Metadata) -> None:
        """Visit DOI."""
        record.add_datafield("024.7..", subfs={"2": "doi", "a": value})
        record.add_datafield(
            "845.4.0.",
            subfs={"3": "Volltext", "u": f"https://doi.org/{value}", "z": "kostenfrei"},
        )

    def visit_filename(self, value: str, _: Marc21Metadata) -> None:
        """Visit filename."""
        self.filename = value

    def visit_title(self, value: str, record: Marc21Metadata) -> None:
        """Visit title."""
        record.emplace_datafield("245.1.0.", subfs={"a": value})

    def visit_year(self, value: str, record: Marc21Metadata) -> None:
        """Visit year."""
        # i think it goes into 245

    def visit_authors(self, value: str, record: Marc21Metadata) -> None:
        """Visit authors."""
        for author in value.split(";"):
            # todo extract affiliation and orcid from author
            record.add_datafield("700.1..", subfs={"a": author})

    def visit_license(self, value: str, record: Marc21Metadata) -> None:
        """Visit license."""
        # 540  |f CC BY-NC-ND |2 cc |u http://creativecommons.org/licenses/by-nc-nd/3.0/at/
        # record.add_datafield("540...", subfs={"f": short, "a": })
