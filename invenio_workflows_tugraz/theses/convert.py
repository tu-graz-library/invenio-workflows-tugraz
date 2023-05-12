# -*- coding: utf-8 -*-
#
# Copyright (C) 2022-2023 Graz University of Technology.
#
# invenio-workflows-tugraz is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Convert from CampusOnline to Marc21."""

from datetime import datetime
from re import split
from xml.etree.ElementTree import Element

from invenio_records_marc21.services.record.metadata import Marc21Metadata, QName


def construct_name(name):
    """Construct name."""
    return f"{name['ln']}, {name['fn']}"


def language_decode(lang):
    """Language decode."""
    languages = {
        "DE": "ger",
        "EN": "eng",
    }
    return languages.get(lang, "PLATZHALTER")


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

    def convert(self, node, record: Marc21Metadata):
        """Convert."""
        self.visit(node, record)


class CampusOnlineToMarc21(Visitor):
    """Convertor from CampusOnline to Marc21."""

    def __init__(self, record: Marc21Metadata):
        """Constructor."""
        super().__init__()
        self.author_name = "N/A"
        self.state = ""
        self.metaclass_name = ""
        self.theses_local_field = {}

        record.emplace_leader("07878nam a2200421 c 4500")
        record.emplace_controlfield("007", "cr#|||||||||||")
        record.emplace_controlfield("008", "230501s########   #####om####|||#|#eng c")
        record.emplace_datafield(
            "040...", subfs={"a": "AT-UBTUG", "b": "ger", "d": "AT-UBTUG", "e": "rda"}
        )
        record.emplace_datafield("044...", subfs={"c": "XA-AT"})
        record.emplace_datafield("264..1.", subfs={"a": "Graz", "c": "DATUM"})
        record.emplace_datafield(
            "300...", subfs={"a": "1 Online-Ressource (Seiten)", "b": "ill"}
        )
        record.emplace_datafield("336...", subfs={"b": "txt"})
        record.emplace_datafield("337...", subfs={"b": "c"})
        record.emplace_datafield("338...", subfs={"b": "cr"})
        record.emplace_datafield("347...", subfs={"a": "Textdatei", "b": "PDF"})
        record.emplace_datafield(
            "506.0..", subfs={"2": "star", "f": "Unrestricted online access"}
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

        # TODO: find out what in 008 should be

    def convert(self, node, record: Marc21Metadata):
        """Override convert."""
        super().convert(node, record)

        for key, subfs in sorted(self.theses_local_field.items()):
            record.emplace_datafield(key, subfs=subfs)

    def visit_ID(self, node, record: Marc21Metadata):
        """Visit ID."""
        record.emplace_datafield(
            "995...", subfs={"i": "TUGRAZonline", "a": str(node.text), "9": "local"}
        )

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
        try:
            year = datetime.strptime(node.text, "%Y-%m-%d %H:%M:%S").year
        except ValueError:
            year = "JAHR"
        self.year = str(year)

    def visit_ORG(self, node: Element, record: Marc21Metadata):
        """Visit ."""

    def visit_ORGP(self, node: Element, record: Marc21Metadata):
        """Visit ."""
        orgp = node.text.split("&gt;")

        faculty = orgp[1] if len(orgp) > 1 else ""
        institute = orgp[2] if len(orgp) > 2 else ""

        self.theses_local_field["971.5.."] = {
            "a": "Technische Universität Graz",
            "b": faculty.strip(),
            "c": institute.strip(),
            "d": "NUMMER",
        }

    def visit_TYPKB(self, node: Element, record: Marc21Metadata):
        """Visit ."""
        value = "HS-DISS" if node.text == "DISS" else "HS-MASTER"
        record.emplace_datafield("970.2..", subfs={"d": value})

    def visit_TYP(self, node: Element, record: Marc21Metadata):
        """Visit ."""
        if self.state == "metaobj":
            self.typ = node.text
            return

        record.emplace_datafield(
            "502...",
            subfs={
                "b": node.text,
                "c": "Technische Universität Graz",
                "d": str(self.year),
            },
        )

    def visit_ZUGKB(self, node: Element, record: Marc21Metadata):
        """Visit ."""

    def visit_ZUG(self, node: Element, record: Marc21Metadata):
        """Visit ."""

    def visit_SPSTAT(self, node: Element, record: Marc21Metadata):
        """Visit ."""

    def visit_SPVON(self, node: Element, record: Marc21Metadata):
        """Visit ."""
        text = node.text
        self.spvon = text if text else ""

    def visit_SPBIS(self, node: Element, record: Marc21Metadata):
        """Visit ."""
        text = node.text

        if not text:
            return

        in_format = "%Y-%m-%d %H:%M:%S"
        out_format = "%d.%m.%Y"

        spvon = datetime.strptime(self.spvon, in_format).strftime(out_format)
        spbis = datetime.strptime(text, in_format).strftime(out_format)

        self.theses_local_field["971.7.."] = {"a": "gesperrt", "b": spvon, "c": spbis}

    def visit_SPBGR(self, node: Element, record: Marc21Metadata):
        """Visit ."""

    def visit_OLANG(self, node: Element, record: Marc21Metadata):
        """Visit ."""
        self.object_language = node.text
        record.emplace_datafield("041...a", value=language_decode(node.text))

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
        self.name = {"fn": "", "ln": ""}

        self.visit(node, record)

        if self.metaclass_name == "AUTHOR":
            self.author_name = self.name
            record.emplace_datafield(
                "100.1..", subfs={"a": construct_name(self.author_name), "4": "aut"}
            )

        if self.metaclass_name == "SUPERVISOR":
            types = {
                "BTEXT": "0",
                "BTTUG": "0",
                "MBTUG": "2",
                "MBEXT": "2",
                "1BUTUG": "1",
                "2BUTUG": "1",
                "3BUTUG": "1",
                "4BUTUG": "1",
                "5BUTUG": "1",
                "6BUTUG": "1",
            }
            ind1 = types.get(self.typ, "")
            self.theses_local_field[f"971.{ind1}.."] = {"a": construct_name(self.name)}

        self.state = ""

    def visit_FN(self, node: Element, record: Marc21Metadata):
        """Visit ."""
        self.name["fn"] = node.text

    def visit_LN(self, node: Element, record: Marc21Metadata):
        """Visit ."""
        self.name["ln"] = node.text

    def visit_FNLN(self, node: Element, record: Marc21Metadata):
        """Visit ."""

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
        text = node.text.replace("\n", " ")
        author = f"{self.author_name['fn']} {self.author_name['ln']}"

        if self.state == "metaobj" and self.language == self.object_language:
            record.emplace_datafield("245.1.0.", subfs={"a": text, "c": author})

        if self.state == "metaobj" and self.language != self.object_language:
            record.emplace_datafield("246.1..", subfs={"i": "TUGRAZonline", "a": text})

    def visit_ABS(self, node: Element, record: Marc21Metadata):
        """Visit ."""
        record.emplace_datafield("520...", value=node.text)

    def visit_KEYW(self, node: Element, record: Marc21Metadata):
        """Visit ."""
        text = node.text
        if not text:
            return

        subjects = filter(
            lambda s: len(s) > 0,
            [s.strip() for s in split(r";|,", text)],
        )

        for subject in subjects:
            record.emplace_datafield("653...", value=subject)

    def visit_LANG(self, node: Element, record: Marc21Metadata):
        """Visit ."""
        self.language = node.text
