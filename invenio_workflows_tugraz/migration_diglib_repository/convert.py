# -*- coding: utf-8 -*-
#
# Copyright (C) 2025-2026 Graz University of Technology.
#
# invenio-workflows-tugraz is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Convert for migrating diglib to repository."""

from collections.abc import Callable
from dataclasses import dataclass
from typing import Literal, cast
from xml.etree.ElementTree import Element

from invenio_records_marc21.services.record.metadata import Marc21Metadata


@dataclass
class Subf:
    """Subf."""

    subfn: str
    subfv: str

    def __init__(self, node: Element) -> None:
        """Construct."""
        self.subfn = node.attrib["subfn"]
        try:
            self.subfv = node.attrib["subfv"]
        except KeyError:
            self.subfv = ""


@dataclass
class Field:
    """Field."""

    fien: str
    ind: str
    subfs: list[Subf]

    def __init__(self, node: Element) -> None:
        """Construct."""
        self.fien = cast(Element, node.find("fien")).attrib["val"]
        self.ind = cast(Element, node.find("ind")).attrib["val"]
        self.subfs = [Subf(subf) for subf in node.findall("subf")]

    def __lt__(self, other: int) -> bool:
        """Less than."""
        return int(self.fien) < other

    def __gt__(self, other: int) -> bool:
        """Greater than."""
        return other < int(self.fien)


class Visitor:
    """Visitor base class."""

    def process(self, node: Element, record: Marc21Metadata) -> None:
        """Execute the corresponding method to the tag name."""

        def func_not_found(fie: Field, __: Marc21Metadata) -> Callable:
            msg = f"NO visitor for field.fien: {fie.fien}"
            raise ValueError(msg)

        field = Field(node)
        fien = "1XX" if 100 < field < 200 else str(field.fien)  # noqa: PLR2004
        visit_func = getattr(self, f"visit_{fien}", func_not_found)
        visit_func(field, record)

    def visit(self, node: Element, record: Marc21Metadata) -> None:
        """Entry point for visitor.

        node: info
        child: fie
        """
        for child in node:
            self.process(child, record)

    def convert(self, node: Element, record: Marc21Metadata) -> None:
        """Convert.

        node: info
        """
        self.visit(node, record)


class MabToMarc21(Visitor):
    """Mab to marc21."""

    def __init__(self, _: Marc21Metadata, publisher: str = "") -> None:
        """Construct."""
        super().__init__()

        self.access: Literal["public", "restricted", "N/A"] = "N/A"
        self.children_ids: list[str] = []
        self.all_child_ids: list[str] = []
        self.directory_name: str = ""
        self.publisher = publisher
        self.filename: str = ""

        # record.emplace_leader("07878nam a2200421 c 4500")
        # record.emplace_controlfield("007", "cr#|||||||||||")
        # # record.emplace_controlfield("008", "230501s????####   #####om####|||#|#### c")
        # record.emplace_datafield(
        #     "040...",
        #     subfs={"a": "AT-UBTUG", "b": "ger", "d": "AT-UBTUG", "e": "rda"},
        # )
        # record.emplace_datafield("044...", subfs={"c": "XA-AT"})

        # record.emplace_datafield(
        #     "300...",
        #     subfs={"a": "1 Online-Ressource (Seiten)", "b": "ill"},
        # )
        # record.emplace_datafield("336...", subfs={"b": "txt"})
        # record.emplace_datafield("337...", subfs={"b": "c"})
        # record.emplace_datafield("338...", subfs={"b": "cr"})
        # record.emplace_datafield("347...", subfs={"a": "Textdatei", "b": "PDF"})

    def convert(self, node: Element, record: Marc21Metadata) -> None:
        """Convert."""
        super().convert(node, record)

        if self.resource_type in ["book", "journal"]:
            record.emplace_datafield(
                "502...",
                subfs={
                    # "b": node.text,
                    "c": self.publisher,
                    "d": self.year,
                },
            )
            record.emplace_datafield(
                "264..1.",
                subfs={"a": "Graz", "b": self.publisher, "c": self.year},
            )

        if self.resource_type == "coverSheet":
            record.emplace_datafield("245.1.0.", subfs={"a": self.resource_type})

    def visit_001(self, field: Field, record: Marc21Metadata) -> None:
        """Visit ."""

    def visit_100(self, field: Field, record: Marc21Metadata) -> None:
        """Visit ."""
        record.emplace_datafield(
            "100.1..",
            subfs={"a": field.subfs[0].subfv, "4": "aut"},
        )

    def visit_1XX(self, field: Field, record: Marc21Metadata) -> None:
        """Visit ."""
        record.add_datafield(
            "700.1..",
            subfs={"a": field.subfs[0].subfv, "4": "aut"},
        )

    def visit_200(self, field: Field, record: Marc21Metadata) -> None:
        """Visit ."""

    def visit_331(self, field: Field, record: Marc21Metadata) -> None:
        """Visit ."""
        record.emplace_datafield("245.1.0.", subfs={"a": field.subfs[0].subfv})

    def visit_334(self, field: Field, record: Marc21Metadata) -> None:
        """Visit ."""

    def visit_335(self, field: Field, record: Marc21Metadata) -> None:
        """Visit ."""

    def visit_341(self, field: Field, record: Marc21Metadata) -> None:
        """Visit ."""

    def visit_343(self, field: Field, record: Marc21Metadata) -> None:
        """Visit ."""

    def visit_359(self, field: Field, record: Marc21Metadata) -> None:
        """Visit ."""

    def visit_405(self, field: Field, record: Marc21Metadata) -> None:
        """Visit ."""

    def visit_406(self, field: Field, record: Marc21Metadata) -> None:
        """Visit ."""

    def visit_410(self, field: Field, record: Marc21Metadata) -> None:
        """Visit ."""

    def visit_412(self, field: Field, record: Marc21Metadata) -> None:
        """Visit ."""

    def visit_425(self, field: Field, _: Marc21Metadata) -> None:
        """Visit ."""
        self.year = field.subfs[0].subfv

    def visit_501(self, field: Field, record: Marc21Metadata) -> None:
        """Visit ."""

    def visit_507(self, field: Field, record: Marc21Metadata) -> None:
        """Visit ."""

    def visit_523(self, field: Field, record: Marc21Metadata) -> None:
        """Visit ."""

    def visit_527(self, field: Field, record: Marc21Metadata) -> None:
        """Visit ."""

    def visit_531(self, field: Field, record: Marc21Metadata) -> None:
        """Visit ."""

    def visit_540(self, field: Field, record: Marc21Metadata) -> None:
        """Visit ."""

    def visit_542(self, field: Field, record: Marc21Metadata) -> None:
        """Visit ."""

    def visit_552(self, field: Field, record: Marc21Metadata) -> None:
        """Visit ."""

    def visit_580(self, field: Field, record: Marc21Metadata) -> None:
        """Visit ."""

    def visit_590(self, field: Field, record: Marc21Metadata) -> None:
        """Visit ."""

    def visit_594(self, field: Field, record: Marc21Metadata) -> None:
        """Visit ."""

    def visit_595(self, field: Field, record: Marc21Metadata) -> None:
        """Visit ."""

    def visit_596(self, field: Field, record: Marc21Metadata) -> None:
        """Visit ."""

    def visit_652(self, field: Field, record: Marc21Metadata) -> None:
        """Visit ."""

    def visit_653(self, field: Field, record: Marc21Metadata) -> None:
        """Visit ."""

    def visit_655(self, field: Field, record: Marc21Metadata) -> None:
        """Visit ."""

    def visit_673(self, field: Field, record: Marc21Metadata) -> None:
        """Visit ."""

    def visit_675(self, field: Field, record: Marc21Metadata) -> None:
        """Visit ."""

    def visit_700(self, field: Field, record: Marc21Metadata) -> None:
        """Visit ."""

    def visit_710(self, field: Field, record: Marc21Metadata) -> None:
        """Visit ."""

    def visit_902(self, field: Field, record: Marc21Metadata) -> None:
        """Visit ."""

    def visit_904(self, field: Field, record: Marc21Metadata) -> None:
        """Visit ."""

    def visit_1000(self, field: Field, record: Marc21Metadata) -> None:
        """Visit ."""

    def visit_1001(self, field: Field, record: Marc21Metadata) -> None:
        """Visit ."""

    def visit_1002(self, field: Field, record: Marc21Metadata) -> None:
        """Visit ."""

    def visit_1003(self, field: Field, record: Marc21Metadata) -> None:
        """Visit ."""

    def visit_1004(self, field: Field, record: Marc21Metadata) -> None:
        """Visit ."""

    def visit_1005(self, field: Field, record: Marc21Metadata) -> None:
        """Visit ."""

    def visit_1006(self, field: Field, record: Marc21Metadata) -> None:
        """Visit ."""

    def visit_1007(self, field: Field, record: Marc21Metadata) -> None:
        """Visit ."""

    def visit_1008(self, field: Field, record: Marc21Metadata) -> None:
        """Visit ."""

    def visit_1009(self, field: Field, record: Marc21Metadata) -> None:
        """Visit ."""

    def visit_1050(self, field: Field, _: Marc21Metadata) -> None:
        """Visit ."""
        self.children_ids = field.subfs[0].subfv.split(" ")

    def visit_1051(self, field: Field, _: Marc21Metadata) -> None:
        """Visit ."""
        self.all_child_ids = field.subfs[0].subfv.split(" ")

    def visit_1052(self, field: Field, _: Marc21Metadata) -> None:
        """Visit ."""
        self.root_id = field.subfs[0].subfv

    def visit_1053(self, field: Field, _: Marc21Metadata) -> None:
        """Visit ."""
        self.parent_id = field.subfs[0].subfv

    def visit_1054(self, field: Field, _: Marc21Metadata) -> None:
        """Visit ."""

    def visit_1055(self, field: Field, _: Marc21Metadata) -> None:
        """Visit ."""

    def visit_1060(self, field: Field, _: Marc21Metadata) -> None:
        """Visit ."""

    def visit_1061(self, field: Field, _: Marc21Metadata) -> None:
        """Visit ."""

    def visit_1062(self, field: Field, _: Marc21Metadata) -> None:
        """Visit ."""

    def visit_1100(self, field: Field, _: Marc21Metadata) -> None:
        """Visit ."""
        match field.subfs[0].subfv:
            case "open" | "openaccess":
                self.access = "public"
            case _:
                self.access = "N/A"

    def visit_1101(self, field: Field, _: Marc21Metadata) -> None:
        """Visit ."""

    def visit_1102(self, field: Field, record: Marc21Metadata) -> None:
        """Visit ."""
        self.resource_type = field.subfs[0].subfv
        record.emplace_datafield(
            "336...",
            subfs={
                "a": field.subfs[0].subfv,
                "2": "repository",
            },
        )

    def visit_1103(self, field: Field, _: Marc21Metadata) -> None:
        """Visit ."""

    def visit_1104(self, field: Field, _: Marc21Metadata) -> None:
        """Visit ."""

    def visit_1105(self, field: Field, _: Marc21Metadata) -> None:
        """Visit ."""
        self.directory_name = field.subfs[0].subfv

    def visit_1106(self, field: Field, _: Marc21Metadata) -> None:
        """Visit ."""

    def visit_1107(self, field: Field, record: Marc21Metadata) -> None:
        """Visit ."""

    def visit_1108(self, field: Field, _: Marc21Metadata) -> None:
        """Visit ."""

    def visit_1109(self, field: Field, _: Marc21Metadata) -> None:
        """Visit ."""

    def visit_1150(self, field: Field, record: Marc21Metadata) -> None:
        """Visit ."""

    def visit_1151(self, field: Field, record: Marc21Metadata) -> None:
        """Visit ."""

    def visit_1152(self, field: Field, record: Marc21Metadata) -> None:
        """Visit ."""

    def visit_1153(self, field: Field, record: Marc21Metadata) -> None:
        """Visit ."""

    def visit_1154(self, field: Field, record: Marc21Metadata) -> None:
        """Visit ."""

    def visit_1155(self, field: Field, record: Marc21Metadata) -> None:
        """Visit ."""

    def visit_1156(self, field: Field, record: Marc21Metadata) -> None:
        """Visit ."""

    def visit_1157(self, field: Field, record: Marc21Metadata) -> None:
        """Visit ."""

    def visit_1158(self, field: Field, record: Marc21Metadata) -> None:
        """Visit ."""

    def visit_1159(self, field: Field, record: Marc21Metadata) -> None:
        """Visit ."""

    def visit_1160(self, field: Field, record: Marc21Metadata) -> None:
        """Visit ."""

    def visit_1161(self, field: Field, record: Marc21Metadata) -> None:
        """Visit ."""

    def visit_1162(self, field: Field, record: Marc21Metadata) -> None:
        """Visit ."""

    def visit_1200(self, field: Field, _: Marc21Metadata) -> None:
        """Visit ."""
        self.filename = field.subfs[0].subfv

    def visit_1203(self, field: Field, _: Marc21Metadata) -> None:
        """Visit ."""

    def visit_1204(self, field: Field, _: Marc21Metadata) -> None:
        """Visit ."""

    def visit_1206(self, field: Field, _: Marc21Metadata) -> None:
        """Visit ."""

    def visit_1207(self, field: Field, _: Marc21Metadata) -> None:
        """Visit ."""

    def visit_1208(self, field: Field, _: Marc21Metadata) -> None:
        """Visit ."""

    def visit_1209(self, field: Field, _: Marc21Metadata) -> None:
        """Visit ."""

    def visit_1210(self, field: Field, _: Marc21Metadata) -> None:
        """Visit ."""

    def visit_1211(self, field: Field, _: Marc21Metadata) -> None:
        """Visit ."""

    def visit_1212(self, field: Field, _: Marc21Metadata) -> None:
        """Visit ."""

    def visit_1213(self, field: Field, _: Marc21Metadata) -> None:
        """Visit ."""

    def visit_1214(self, field: Field, _: Marc21Metadata) -> None:
        """Visit ."""

    def visit_1215(self, field: Field, _: Marc21Metadata) -> None:
        """Visit ."""

    def visit_1250(self, field: Field, _: Marc21Metadata) -> None:
        """Visit ."""

    def visit_1301(self, field: Field, record: Marc21Metadata) -> None:
        """Visit ."""

    def visit_1302(self, field: Field, record: Marc21Metadata) -> None:
        """Visit ."""

    def visit_1303(self, field: Field, record: Marc21Metadata) -> None:
        """Visit ."""
        # TODO:
        # should go into marc21 metadata

    def visit_1400(self, field: Field, record: Marc21Metadata) -> None:
        """Visit ."""
        # TODO:
        # should go into marc21 metadata

    def visit_1401(self, field: Field, record: Marc21Metadata) -> None:
        """Visit ."""
        self.directory_name = field.subfs[0].subfv
        record.emplace_datafield("245.1.0.", subfs={"a": field.subfs[0].subfv})

    def visit_1402(self, field: Field, record: Marc21Metadata) -> None:
        """Visit ."""
        issue = int(field.subfs[0].subfv)
        self.directory_name = f"{issue:02d}"
        record.emplace_datafield("245.1.0.", subfs={"a": field.subfs[0].subfv})

    def visit_1403(self, field: Field, record: Marc21Metadata) -> None:
        """Visit ."""

    def visit_1404(self, field: Field, record: Marc21Metadata) -> None:
        """Visit ."""

    def visit_1405(self, field: Field, record: Marc21Metadata) -> None:
        """Visit ."""

    def visit_1406(self, field: Field, record: Marc21Metadata) -> None:
        """Visit ."""

    def visit_1407(self, field: Field, record: Marc21Metadata) -> None:
        """Visit ."""

    def visit_1408(self, field: Field, record: Marc21Metadata) -> None:
        """Visit ."""

    def visit_1409(self, field: Field, record: Marc21Metadata) -> None:
        """Visit ."""

    def visit_1410(self, field: Field, record: Marc21Metadata) -> None:
        """Visit ."""

    def visit_1411(self, field: Field, record: Marc21Metadata) -> None:
        """Visit ."""

    def visit_1450(self, field: Field, record: Marc21Metadata) -> None:
        """Visit ."""

    def visit_1451(self, field: Field, record: Marc21Metadata) -> None:
        """Visit ."""

    def visit_1452(self, field: Field, record: Marc21Metadata) -> None:
        """Visit ."""

    def visit_1453(self, field: Field, record: Marc21Metadata) -> None:
        """Visit ."""

    def visit_1454(self, field: Field, record: Marc21Metadata) -> None:
        """Visit ."""
        # TODO:
        # should go into marc21 metadata

    def visit_1455(self, field: Field, record: Marc21Metadata) -> None:
        """Visit ."""

    def visit_1456(self, field: Field, record: Marc21Metadata) -> None:
        """Visit ."""

    def visit_1457(self, field: Field, record: Marc21Metadata) -> None:
        """Visit ."""

    def visit_1458(self, field: Field, record: Marc21Metadata) -> None:
        """Visit ."""
        # TODO:
        # should go into marc21 metadata

    def visit_1500(self, field: Field, record: Marc21Metadata) -> None:
        """Visit ."""
        # TODO:
        # should go into marc21 metadata

    def visit_1501(self, field: Field, record: Marc21Metadata) -> None:
        """Visit ."""

    def visit_1502(self, field: Field, record: Marc21Metadata) -> None:
        """Visit ."""

    def visit_1503(self, field: Field, record: Marc21Metadata) -> None:
        """Visit ."""

    def visit_1504(self, field: Field, _: Marc21Metadata) -> None:
        """Visit ."""
        # TODO:
        # should go into marc21 metadata
        self.publisher = field.subfs[0].subfv

    def visit_1505(self, field: Field, record: Marc21Metadata) -> None:
        """Visit ."""

    def visit_1506(self, field: Field, record: Marc21Metadata) -> None:
        """Visit ."""

    def visit_1507(self, field: Field, record: Marc21Metadata) -> None:
        """Visit ."""

    def visit_1508(self, field: Field, record: Marc21Metadata) -> None:
        """Visit ."""

    def visit_1509(self, field: Field, record: Marc21Metadata) -> None:
        """Visit ."""

    def visit_1550(self, field: Field, record: Marc21Metadata) -> None:
        """Visit ."""

    def visit_1551(self, field: Field, record: Marc21Metadata) -> None:
        """Visit ."""

    def visit_1552(self, field: Field, record: Marc21Metadata) -> None:
        """Visit ."""

    def visit_1553(self, field: Field, record: Marc21Metadata) -> None:
        """Visit ."""

    def visit_1554(self, field: Field, record: Marc21Metadata) -> None:
        """Visit ."""

    def visit_1600(self, field: Field, record: Marc21Metadata) -> None:
        """Visit ."""

    def visit_1601(self, field: Field, record: Marc21Metadata) -> None:
        """Visit ."""

    def visit_1602(self, field: Field, record: Marc21Metadata) -> None:
        """Visit ."""

    def visit_1603(self, field: Field, record: Marc21Metadata) -> None:
        """Visit ."""

    def visit_1604(self, field: Field, record: Marc21Metadata) -> None:
        """Visit ."""

    def visit_1700(self, field: Field, record: Marc21Metadata) -> None:
        """Visit ."""

    def visit_1701(self, field: Field, record: Marc21Metadata) -> None:
        """Visit ."""
        # TODO:
        # should go into marc21 metadata

    def visit_1702(self, field: Field, record: Marc21Metadata) -> None:
        """Visit ."""

    def visit_1703(self, field: Field, record: Marc21Metadata) -> None:
        """Visit ."""

    def visit_1704(self, field: Field, record: Marc21Metadata) -> None:
        """Visit ."""

    def visit_1705(self, field: Field, record: Marc21Metadata) -> None:
        """Visit ."""

    def visit_1706(self, field: Field, record: Marc21Metadata) -> None:
        """Visit ."""

    def visit_1707(self, field: Field, record: Marc21Metadata) -> None:
        """Visit ."""

    def visit_1708(self, field: Field, record: Marc21Metadata) -> None:
        """Visit ."""

    def visit_1709(self, field: Field, record: Marc21Metadata) -> None:
        """Visit ."""

    def visit_1800(self, field: Field, record: Marc21Metadata) -> None:
        """Visit ."""

    def visit_1801(self, field: Field, record: Marc21Metadata) -> None:
        """Visit ."""

    def visit_1802(self, field: Field, record: Marc21Metadata) -> None:
        """Visit ."""

    def visit_1803(self, field: Field, record: Marc21Metadata) -> None:
        """Visit ."""

    def visit_1804(self, field: Field, record: Marc21Metadata) -> None:
        """Visit ."""

    def visit_1805(self, field: Field, record: Marc21Metadata) -> None:
        """Visit ."""

    def visit_1806(self, field: Field, record: Marc21Metadata) -> None:
        """Visit ."""

    def visit_1807(self, field: Field, record: Marc21Metadata) -> None:
        """Visit ."""
