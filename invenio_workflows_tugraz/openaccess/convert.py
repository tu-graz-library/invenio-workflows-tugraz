# -*- coding: utf-8 -*-
#
# Copyright (C) 2022-2025 Graz University of Technology.
#
# invenio-workflows-tugraz is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Open Access Workflow."""

from contextlib import suppress
from json import load
from pathlib import Path

from invenio_records_marc21 import Marc21Metadata


class Converter:
    """Converter base class to convert one format into another."""

    def __init__(self) -> None:
        """Construct of the class."""
        # Cache iso639-3 language codes to dict
        self.languages = self.initialize_languages()

    def initialize_languages(self) -> dict:
        """Initialize language cache dictionary."""
        path = Path(__file__).parent / "../data/iso6393.json"

        with Path(path).open() as fp:
            languages = filter(lambda obj: "iso6393" in obj, load(fp))

        return {language["name"]: language["iso6393"] for language in languages}

    def convert(self, value: object, record: Marc21Metadata) -> None:
        """Convert record from Pure JSON format to MARC21XML."""
        for attribute, val in value.items():
            self.convert_attribute(attribute, val, record)

    def convert_attribute(
        self,
        attribute: str,
        value: object,
        record: Marc21Metadata,
    ) -> None:
        """Traverse first level elements of dictionary and extract attributes."""
        convert_function = getattr(self, f"convert_{attribute}", lambda _, __: None)
        convert_function(value, record)


class Pure2Marc21(Converter):
    """Pure to marc21 converter class."""

    def convert_abstract(self, value: dict, record: Marc21Metadata) -> None:
        """Add the abstract to the Marc21Metadata."""
        try:
            abstract = value["de_DE"]
        except KeyError:
            try:
                abstract = value["en_GB"]
            except KeyError:
                abstract = None

        if abstract:
            record.emplace_datafield("520...", value=abstract)

    def convert_additionalLinks(self, value: list, record: Marc21Metadata) -> None:
        """Add the additionalLinks attribute to the Marc21Metadata."""
        for link in value:
            if "url" in link:
                record.emplace_datafield("856.4.1.u", value=link["url"])

    def convert_bibliographicalNote(self, value: dict, record: Marc21Metadata) -> None:
        """Add the bibliographicalNote attribute to the Marc21Metadata."""
        try:
            text = value["de_DE"]
        except KeyError:
            try:
                text = value["en_GB"]
            except KeyError:
                text = None
        if text:
            record.emplace_datafield("500...", value=text)

    def convert_edition(self, value: str, record: Marc21Metadata) -> None:
        """Add the edition attribute to the Marc21Metadata."""
        record.emplace_datafield("250...", value=value)

    def convert_electronicIsbns(self, value: list, record: Marc21Metadata) -> None:
        """Add the electronicIsbns attribute to the Marc21Metadata."""
        record.emplace_datafield("020...", value=str(value[0]).strip())

    def convert_event(self, value: dict, record: Marc21Metadata) -> None:
        """Add the event attribute to the Marc21Metadata."""
        if "name" not in value:
            return

        for event_name in value["name"]["text"]:
            record.emplace_datafield("711.2..", value=event_name["value"])

    def convert_isbns(self, value: list, record: Marc21Metadata) -> None:
        """Add the isbns attribute to the Marc21Metadata."""
        for isbn in value:
            record.emplace_datafield("020...", value=isbn)

    def convert_journalAssociation(self, value: dict, record: Marc21Metadata) -> None:
        """Add the journalAssociation attribute to the Marc21Metadata."""
        subfs = {}

        with suppress(KeyError):
            subfs["t"] = value["title"]["title"]
        with suppress(KeyError):
            subfs["x"] = value["issn"]["issn"]

        if subfs:
            record.emplace_datafield("773.0.8.", subfs=subfs)

    def convert_journalNumber(self, value: str, record: Marc21Metadata) -> None:
        """Add the journalNumber attribute to the Marc21Metadata."""
        record.emplace_datafield("773.0.8.g", value=value)

    def convert_keywordGroups(self, value: list, record: Marc21Metadata) -> None:
        """Add the keywordGroups attribute to the Marc21Metadata."""
        for item in value:
            keyword_group = KeywordGroup()
            keyword_group.convert(item, record)

    def convert_language(self, value: dict, record: Marc21Metadata) -> None:
        """Add the language attribute to the Marc21Metadata."""
        language = value["term"]["en_GB"]
        language_iso6393 = self.languages[language]
        record.emplace_datafield("041...", value=language_iso6393)

    def convert_managingOrganisationalUnit(
        self,
        value: dict,
        record: Marc21Metadata,
    ) -> None:
        """Add the managingOrganisationalUnit attribute to the Marc21Metadata."""
        for locale in value["name"]["text"]:
            record.emplace_unique_field("100.1..u", value=locale["value"])
            record.emplace_unique_field("700.1..u", value=locale["value"])

    def convert_numberOfPages(self, value: int, record: Marc21Metadata) -> None:
        """Add the numberOfPages attribute to the Marc21Metadata."""
        record.emplace_datafield("300...", value=str(value))

    def convert_organisationalUnits(self, value: list, record: Marc21Metadata) -> None:
        """Add the organisationalUnits attribute to the Marc21Metadata."""
        for o_unit in value:
            for locale in o_unit["name"]["text"]:
                record.emplace_unique_field("100.1..u", value=locale["value"])
                record.emplace_unique_field("700.1..u", value=locale["value"])

    def convert_pages(self, value: str, record: Marc21Metadata) -> None:
        """Add the pages attriute to the Marc21Metadata."""
        pages = value
        record.emplace_datafield("300...", value=pages)

    def convert_patentNumber(self, value: str, record: Marc21Metadata) -> None:
        """Add the patentNumber attribute to the Marc21Metadata."""
        record.emplace_datafield("013...", value=value)

    def convert_peerReview(
        self,
        value: bool,  # noqa: FBT001
        record: Marc21Metadata,
    ) -> None:
        """Add the peerReview attribute to the Marc21Metadata."""
        if value:
            status = "Refereed/Peer-reviewed"
            record.emplace_datafield("500...", value=status)

    def convert_placeOfPublication(self, value: str, record: Marc21Metadata) -> None:
        """Add the placeOfPublication attribute to the Marc21Metadata."""
        record.emplace_datafield("264..1.", value=value)

    def convert_publicationSeries(self, value: list, record: Marc21Metadata) -> None:
        """Add the publicationSeries attribute to the Marc21Metadata."""
        for series in value:
            record.emplace_datafield("490.0..", value=series["name"])

    def convert_publicationStatuses(self, value: list, record: Marc21Metadata) -> None:
        """Add the publicationStatuses attribute to the Marc21Metadata."""
        for entry in value:
            publication_status = PublicationStatus()
            publication_status.convert(entry, record)

    def convert_publisher(self, value: dict, record: Marc21Metadata) -> None:
        """Add the publisher attribute to the Marc21Metadata."""
        # TODO:
        # maybe think of moving the code about getting the publisher information
        # over the pure_service which is now in the import_func function to here

    def convert_relatedProjects(self, value: list, record: Marc21Metadata) -> None:
        """Add the relatedProjects attribute to the Marc21Metadata."""
        for entry in value:
            for locale in entry["name"]["text"]:
                record.emplace_datafield("536...", value=locale["value"])

    def convert_subTitle(self, value: dict, record: Marc21Metadata) -> None:
        """Add the subTitle attribute to the Marc21Metadata."""
        record.emplace_datafield("245.1.0.b", value=value["value"])

    def convert_title(self, value: dict, record: Marc21Metadata) -> None:
        """Add the title attribute to the Marc21Metadata."""
        record.emplace_datafield("245.1.0.", value=value["value"])

    def convert_volume(self, value: str, record: Marc21Metadata) -> None:
        """Add the volume attribute to the Marc21Metadata."""
        record.emplace_datafield("490.0..", value=value)
        record.emplace_datafield("773.0.8.g", value=value)


class KeywordGroup(Converter):
    """Class to convert the keywordgroup attribute."""

    def convert_keywordContainers(self, value: list, record: Marc21Metadata) -> None:
        """Add keywords."""
        for item in value:
            self.convert(item, record)

    def convert_freeKeywords(self, value: list, record: Marc21Metadata) -> None:
        """Add free keywords."""
        for free_keyword in value:
            for word in free_keyword["freeKeywords"]:
                record.emplace_datafield("650..4.g", value=word)

    def convert_structuredKeyword(self, value: dict, record: Marc21Metadata) -> None:
        """Add free keywords."""
        for word in value["term"]["text"]:
            record.emplace_datafield("650..4.", value=word["value"])


class PublicationStatus(Converter):
    """Class to convert publication status."""

    def convert_publicationDate(self, value: dict, record: Marc21Metadata) -> None:
        """Add the publication date to the Marc21Metadata."""
        # without cast not serializable
        record.emplace_datafield("264..1.c", value=str(value["year"]))

    def convert_publicationStatus(self, value: dict, record: Marc21Metadata) -> None:
        """Add the publication status to the Marc21Metadata."""
        record.emplace_datafield("250...", value=value["term"]["de_DE"])
