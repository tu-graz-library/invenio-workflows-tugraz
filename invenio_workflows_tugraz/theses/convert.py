# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Graz University of Technology.
#
# invenio-workflows-tugraz is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Convert from CampusOnline to Marc21."""

from xml.etree.ElementTree import Element

from invenio_records_marc21.services.record.metadata import Marc21Metadata, QName


class Visitor:
    """Visitor base class."""

    def process(self, node: Element, record: Marc21Metadata):
        """Execute the corresponding method to the tag name."""

        def func_not_found(*args, **kwargs):
            localname = QName(node).localname
            namespace = QName(node).namespace
            raise ValueError(f"NO visitor node: '{localname}' ns: '{namespace}'")

        tag_name = QName(node).localname
        visit_func = getattr(self, f"visit_{tag_name}", func_not_found)
        result = visit_func(node, record)
        return result

    def visit_attr(self, node, record: Marc21Metadata):
        """Base function for attr."""
        key = node.attrib["key"]

        def func_not_found(*args, **kwargs):
            raise ValueError(f"NO visitor node: '{key}'")

        visit_func = getattr(self, f"visit_{key}", func_not_found)
        result = visit_func(node, record)
        return result

    def visit(self, node, record: Marc21Metadata):
        """Entry point for visitor."""
        for child in node:
            self.process(child, record)


class CampusOnlineToMarc21(Visitor):
    """Convertor from CampusOnline to Marc21."""

    def __init__(self):
        """Constructor."""
        super().__init__()
        self.author_name = "N/A"

    def visit_ID(self, node, record: Marc21Metadata):
        """Visit ID."""
        record.emplace_datafield("970.0.1.a", value=node.text)

    def visit_PAG(self, node, record: Marc21Metadata):
        """Visit PAG."""

    def visit_CO(self, node: Element, record: Marc21Metadata):
        """Visit CO."""

    def visit_CHD(self, node: Element, record: Marc21Metadata):
        """Visit CHD."""

    def visit_EJAHR(self, node: Element, record: Marc21Metadata):
        """Visit EJAHR."""

    def visit_ARCHD(self, node: Element, record: Marc21Metadata):
        """Visit ARCHD."""

    def visit_PUBD(self, node: Element, record: Marc21Metadata):
        """Visit PUBD."""

    def visit_PUBLIC(self, node: Element, record: Marc21Metadata):
        """Visit PUBLIC."""

    def visit_STATUS(self, node: Element, record: Marc21Metadata):
        """Visit status."""

    def visit_STATUSD(self, node: Element, record: Marc21Metadata):
        """Visit Status date."""

    def visit_ORG(self, node: Element, record: Marc21Metadata):
        """Visit ."""

    def visit_ORGP(self, node: Element, record: Marc21Metadata):
        """Visit ."""
        institute, institute_english, institute_number, *_ = node.text.split("&gt;")
        record.emplace_datafield(
            "971.5..",
            subfs={
                "a": "Technische Universität Graz",
                "b": institute,
                "c": institute_english,
                "d": institute_number,
            },
        )

    def visit_TYPKB(self, node: Element, record: Marc21Metadata):
        """Visit ."""

    def visit_TYP(self, node: Element, record: Marc21Metadata):
        """Visit ."""
        record.emplace_datafield(
            "502...",
            subfs={"b": node.text, "c": "Technische Universität Graz"},
        )

    def visit_ZUGKB(self, node: Element, record: Marc21Metadata):
        """Visit ."""

    def visit_ZUG(self, node: Element, record: Marc21Metadata):
        """Visit ."""

    def visit_SPSTAT(self, node: Element, record: Marc21Metadata):
        """Visit ."""

    def visit_SPVON(self, node: Element, record: Marc21Metadata):
        """Visit ."""

    def visit_SPBIS(self, node: Element, record: Marc21Metadata):
        """Visit ."""

    def visit_SPBGR(self, node: Element, record: Marc21Metadata):
        """Visit ."""

    def visit_OLANG(self, node: Element, record: Marc21Metadata):
        """Visit ."""

    def visit_TLANGS(self, node: Element, record: Marc21Metadata):
        """Visit ."""

    def visit_VOLLTEXT(self, node: Element, record: Marc21Metadata):
        """Visit ."""

    def visit_metaclass(self, node: Element, record: Marc21Metadata):
        """Visit ."""
        self.visit(node, record)

    def visit_name(self, node: Element, record: Marc21Metadata):
        """Visit ."""
        self.metaclass_name = node.text

    def visit_metaobj(self, node: Element, record: Marc21Metadata):
        """Visit ."""
        if self.metaclass_name not in ["AUTHOR", "TEXT", "SUPERVISOR"]:
            return

        self.state = "metaobj"
        self.visit(node, record)
        self.state = ""

    def visit_FN(self, node: Element, record: Marc21Metadata):
        """Visit ."""

    def visit_LN(self, node: Element, record: Marc21Metadata):
        """Visit ."""

    def visit_FNLN(self, node: Element, record: Marc21Metadata):
        """Visit ."""
        if self.metaclass_name == "AUTHOR":
            self.author_name = node.text
            record.emplace_datafield("100.1..", value=self.author_name)
        if self.metaclass_name == "SUPERVISOR":
            record.emplace_datafield("971..0.a", value=node.text)

    def visit_AKK(self, node: Element, record: Marc21Metadata):
        """Visit ."""

    def visit_MNR(self, node: Element, record: Marc21Metadata):
        """Visit ."""

    def visit_STRI(self, node: Element, record: Marc21Metadata):
        """Visit ."""

    def visit_STKZ(self, node: Element, record: Marc21Metadata):
        """Visit ."""

    def visit_ORIG(self, node: Element, record: Marc21Metadata):
        """Visit ."""

    def visit_INTERN(self, node: Element, record: Marc21Metadata):
        """Visit ."""

    def visit_TIT(self, node: Element, record: Marc21Metadata):
        """Visit ."""
        if self.state == "metaobj" and self.language == "DE":
            record.emplace_datafield(
                "245.1.0.", subfs={"a": node.text, "c": self.author_name}
            )

    def visit_ABS(self, node: Element, record: Marc21Metadata):
        """Visit ."""

    def visit_KEYW(self, node: Element, record: Marc21Metadata):
        """Visit ."""

    def visit_LANG(self, node: Element, record: Marc21Metadata):
        """Visit ."""
        self.language = node.text
