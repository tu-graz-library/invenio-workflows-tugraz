# -*- coding: utf-8 -*-
#
# Copyright (C) 2024-2025 Graz University of Technology.
#
# invenio-workflows-tugraz is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Convert from LOM to Marc21."""

from datetime import datetime

from invenio_records_marc21.services.record.metadata import Marc21Metadata


class Visitor:
    """Visitor base class."""

    def visit(self, value: dict, record: Marc21Metadata) -> None:
        """Convert record from LOM JSON format to MARC21XML."""
        for attribute, val in value.items():
            self.visit_attribute(attribute, val, record)

    def visit_attribute(
        self,
        attribute: str,
        value: dict,
        record: Marc21Metadata,
    ) -> None:
        """Traverse first level elements of dictionary and extract attributes."""

        def func_not_found(*_: dict, **__: dict) -> None:
            msg = f"NO visitor node: '{attribute}'"
            raise ValueError(msg)

        visit_function = getattr(self, f"visit_{attribute}", func_not_found)
        return visit_function(value, record)


class LOM2Marc21(Visitor):
    """LOM to Marc21 converter class."""

    def __init__(self, record: Marc21Metadata, doi: str) -> None:
        """Construct."""
        super().__init__()

        record.emplace_leader("07878nai a2200421 c 4500")
        record.emplace_controlfield("007", "ccr|||||||||||")
        record.emplace_datafield("024.7.0.", subfs={"a": doi, "2": "doi"})
        record.emplace_datafield("040.0.0.", subfs={"b": "ger", "e": "rda"})
        record.emplace_datafield("044.0.0.", subfs={"c": "XA-AT"})
        record.emplace_datafield("336.0.0.", subfs={"b": "txt"})
        record.add_datafield("336.0.0.", subfs={"b": "tdi"})
        record.emplace_datafield("337.0.0.", subfs={"b": "c"})
        record.emplace_datafield("338.0.0.", subfs={"b": "cr"})
        record.emplace_datafield("347.0.0.", subfs={"a": "Textdatei"})
        record.add_datafield("347.0.0.", subfs={"a": "Videodatei"})
        record.emplace_datafield("500.0.0.", subfs={"a": "Gesehen am"})
        record.emplace_datafield(
            "506.0.0.",
            subfs={"f": "Unrestricted online access", "2": "star"},
        )
        record.emplace_datafield(
            "655.0.7.",
            subfs={
                "a": "Massive Open Online Course",
                "0": "$$0 (DE-588)107372798X",
                "2": "gnd-content",
            },
        )
        record.emplace_datafield(
            "995...",
            subfs={"i": "TU Graz Repository", "a": doi, "9": "local"},
        )

        self.title = ""
        self.entities = []

    def visit(self, value: dict, record: Marc21Metadata) -> None:
        """Visit."""
        super().visit(value, record)

        if self.title == "":
            return

        subfs = {"a": self.title}

        if len(self.entities) > 0:
            subfs["c"] = ",".join(self.entities[0]["name"])

        record.emplace_datafield(
            "245.0.0.",
            subfs=subfs,
        )

    def visit_general(self, value: dict, record: Marc21Metadata) -> None:
        """Process General."""
        super().visit(value, record)

    def visit_title(self, value: dict, _: Marc21Metadata) -> None:
        """Process ."""
        self.title = value["langstring"]["#text"]

    def visit_language(self, value: str, record: Marc21Metadata) -> None:
        """Process ."""
        for language in value:
            record.add_datafield("041.0.0.", subfs={"a": language})

    def visit_description(self, value: list, record: Marc21Metadata) -> None:
        """Process ."""
        for description in value:
            text = description["langstring"]["#text"]
            record.add_datafield("520.0.0.", subfs={"a": text})

    def visit_educational_description(
        self,
        value: list,
        record: Marc21Metadata,
    ) -> None:
        """Process ."""
        for description in value:
            text = description["langstring"]["#text"]
            record.add_datafield("521.0.0.", subfs={"a": text})

    def visit_technical(self, value: dict, record: Marc21Metadata) -> None:
        """Process technical."""
        super().visit(value, record)

    def visit_thumbnail(self, value: dict, record: Marc21Metadata) -> None:
        """Process thumbnail."""
        super().visit(value, record)

    def visit_licenses(self, value: dict, record: Marc21Metadata) -> None:
        """Process licenses."""
        try:
            id_ = value["id"]
        except KeyError:
            id_ = None

        try:
            url = value["url"]
        except KeyError:
            url = None

        if id_ is None or url is None:
            return

        record.emplace_datafield(
            "540.0.0.",
            subfs={
                "2": "cc",
                "a": "Thumbnail",
                "f": id_,
                "u": url,
            },
        )

    def visit_location(self, value: dict, record: Marc21Metadata) -> None:
        """Process location."""
        text = value["#text"]
        record.emplace_datafield(
            "856.4.0.",
            subfs={"u": text, "x": "IMOOX", "z": "kostenfrei", "3": "Volltext"},
        )

    def visit_duration(self, value: dict, record: Marc21Metadata) -> None:
        """Process duration."""
        # TODO nachfragen
        # record.emplace_datafield("300.0.0.", subfs={"a": "Online-Ressource"})

    def visit_educational(self, value: dict, record: Marc21Metadata) -> None:
        """Process educational."""
        if "description" in value:
            self.visit_educational_description(value["description"], record)
            del value["description"]

        super().visit(value, record)

    def visit_rights(self, value: dict, record: Marc21Metadata) -> None:
        """Process rights."""
        super().visit(value, record)

    def visit_url(self, value: str, record: Marc21Metadata) -> None:
        """Process url."""
        record.emplace_datafield("540.0.0.", subfs={"a": "MOOC", "u": value, "2": "cc"})

    def visit_classification(self, value: dict, record: Marc21Metadata) -> None:
        """Process classification."""
        super().visit(value, record)

    def visit_lifecycle(self, value: dict, record: Marc21Metadata) -> None:
        """Process lifecycle."""
        super().visit(value, record)

    def visit_datetime(self, value: str, record: Marc21Metadata) -> None:
        """Process datetime."""
        dt = datetime.strptime(value, "%Y-%m-%d %H:%M:%S")
        startdate = value
        record.emplace_datafield(
            "264.3.1.",
            subfs={"a": "Graz", "b": "Technische Universität Graz", "c": startdate},
        )
        record.emplace_controlfield(
            "008",
            f"230501c{dt.year}9999   #####o#####|||#|2### #",
        )
        # TODO empty_expected

    def visit_contribute(self, value: list, record: Marc21Metadata) -> None:
        """Process contribute."""
        for contribute in value:
            description = contribute["date"]["description"]["langstring"]["#text"]
            role = contribute["role"]["value"]["langstring"]["#text"]
            entities = contribute["entity"]

            for entity in entities:
                self.entities += [{"name": entity, "role": role}]
            record.emplace_datafield("545.0.0.", subfs={"a": description})

        for idx, x in enumerate(self.entities):
            if idx == 0:
                record.emplace_datafield("100.1.0.", subfs={"a": x["name"], "4": "aut"})
            else:
                record.emplace_datafield(
                    "700.1.0.",
                    subfs={
                        "a": x["name"],
                        "4": x["role"],
                    },
                )
