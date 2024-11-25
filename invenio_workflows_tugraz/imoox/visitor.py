# -*- coding: utf-8 -*-
#
# Copyright (C) 2022-2024 Graz University of Technology.
#
# invenio-workflows-tugraz is free software; you can redistribute it
# and/or modify it under the terms of the MIT License; see LICENSE
# file for more details.

"""Converter Module to facilitate conversion of metadata."""

from contextlib import suppress

from invenio_records_lom.utils import LOMMetadata


def langstring(value: str, language: str = "x-none") -> dict:
    """Langstring."""
    return {
        "langstring": {
            "lang": language,
            "#text": value,
        },
    }


class Converter:
    """Converter base class."""

    def convert(self, parent: dict, record: LOMMetadata) -> None:
        """Convert method."""
        for attribute, value in parent.items():
            self.process(attribute, value, record)

    def process[T](self, attribute: str, value: T, record: LOMMetadata) -> None:
        """Execute the corresponding method to the attribute."""

        def func_not_found(*_: dict, **__: dict) -> None:
            msg = f"NO convert method for {attribute}"
            raise ValueError(msg)

        convert_func = getattr(self, f"convert_{attribute}", func_not_found)
        return convert_func(value, record)


class IMOOXToLOM(Converter):
    """Convert class to convert Mooc to LOM."""

    def __init__(self) -> None:
        """Construct MoocToLOM."""
        self.language = ""

    def set_language(self, parent: dict) -> None:
        """Set default language for langstring."""
        if "languages" not in parent["attributes"]:
            return

        if len(parent["attributes"]["languages"]) == 0:
            return

        self.language = parent["attributes"]["languages"][0]

    def append_contribute(
        self,
        contributors: list,
        record: LOMMetadata,
        default_role: str = "",
    ) -> None:
        """Append to contribute."""
        for contributor in contributors:
            try:
                description = contributor["description"]
            except KeyError:
                description = None

            try:
                role = contributor["type"]
            except KeyError:
                role = default_role

            record.append_contribute(
                name=contributor["name"],
                role=role,
                description=description,
            )

    def convert(self, parent: dict, record: LOMMetadata) -> None:
        """Convert overrides base convert method to return the record."""
        self.set_language(parent)

        super().convert(parent, record)

    def convert_id(self, value: str, record: LOMMetadata) -> None:
        """Convert id attribute."""
        record.append_identifier(id_=value, catalog="imoox")

    def convert_courseCode(self, value: str, record: LOMMetadata) -> None:
        """Convert courseCode attribute."""
        record.append_identifier(id_=value, catalog="imoox")

    def convert_attributes(self, value: dict, record: LOMMetadata) -> None:
        """Convert attributes attribute."""
        super().convert(value, record)

    def convert_name(self, value: str, record: LOMMetadata) -> None:
        """Convert name attribute."""
        record.set_title(title=value, language_code=self.language)

    def convert_abstract(self, value: str, record: LOMMetadata) -> None:
        """Convert abstract attribute."""
        record.append_description(description=value, language_code=self.language)

    def convert_description(self, value: str, record: LOMMetadata) -> None:
        """Convert description attribute."""
        record.append_description(description=value, language_code=self.language)

    def convert_inLanguage(self, value: list, record: LOMMetadata) -> None:
        """Convert language attribute."""
        for lang in value:
            record.append_language(lang)

    def convert_startDate(self, value: str, record: LOMMetadata) -> None:
        """Convert startDate attribute."""
        record.set_datetime(value[0].split("T")[0])

    def convert_image(self, value: dict, record: LOMMetadata) -> None:
        """Convert image attribute."""
        record.set_thumbnail(value)

    def convert_instructor(self, value: list[dict], record: LOMMetadata) -> None:
        """Convert instructor attribute."""
        self.append_contribute(value, record, default_role="Author")

    def convert_learningobjectives(self, value: str, record: LOMMetadata) -> None:
        """Convert learningobjectives attribute."""
        for desc in value:
            record.append_educational_desription(
                description=desc,
                language_code=self.langugage,
            )

    def convert_duration(self, value: str, record: LOMMetadata) -> None:
        """Convert duration attribute."""
        record.set_duration(value=value, language=self.language)

    def convert_partnerInstitute(self, value: list[dict], record: LOMMetadata) -> None:
        """Convert partnerInstitute attribute."""
        self.append_contribute(value, record, default_role="Publisher")

    def convert_moocProvider(self, value: dict, record: LOMMetadata) -> None:
        """Convert moocProvider attribute."""
        record.append_metametadata_contribute(
            name=value["name"],
            url="",
            logo="",
            role="Provider",
        )

    def convert_url(self, value: str, record: LOMMetadata) -> None:
        """Convert url attribute."""
        record.set_location(value)

    def convert_workload(self, value: str, record: LOMMetadata) -> None:
        """Convert workload attribute."""
        record.set_typical_learning_time(value, description="workload")

    def convert_courseLicenses(self, value: list, record: LOMMetadata) -> None:
        """Convert courseLicenses attribute."""
        record.set_rights_url(url=value[0]["url"])

    def convert_license(self, value: list, record: LOMMetadata) -> None:
        """Convert courseLicense attribute."""
        record.set_rights_url(url=value[0]["url"])

    def convert_categories(self, value: dict, record: LOMMetadata) -> None:
        """Convert categories attribute."""
        super().convert(value, record)

    def convert_contributor(self, value: list[dict], record: LOMMetadata) -> None:
        """Convert contributor."""
        self.append_contribute(value, record)

    def convert_publisher(self, value: dict, record: LOMMetadata) -> None:
        """Convert publisher."""
        self.append_contribute([value], record)

    def convert_educationalAlignment(
        self,
        value: list[dict],
        record: LOMMetadata,
    ) -> None:
        """Convert educationalAlignment."""
        for item in value:
            for subitem in item["name"]:
                with suppress(KeyError):
                    record.append_oefos_id(
                        oefos_id=item["shortCode"],
                        language_code=subitem["inLanguage"],
                    )

    def convert_creator(self, value: list[dict], record: LOMMetadata) -> None:
        """Convert creator."""
        self.append_contribute(value, record)

    ####
    #
    # those categories are not mapped to lom
    #
    ####

    def convert_type(self, value: str, record: LOMMetadata) -> None:
        """Convert type attribute."""

    def convert_courseMode(self, value: dict[list], record: LOMMetadata) -> None:
        """Convert courseMode attribute."""

    def convert_availableUntil(self, value: str, record: LOMMetadata) -> None:
        """Convert availableUntil attribute."""

    def convert_endDate(self, value: str, record: LOMMetadata) -> None:
        """Convert endDate attribute."""
        # see startDate

    def convert_video(self, value: str, record: LOMMetadata) -> None:
        """Convert video attribute."""

    def convert_access(self, value: dict[list], record: LOMMetadata) -> None:
        """Convert access attribute."""

    def convert_learningResourceType(self, value: dict, record: LOMMetadata) -> None:
        """Convert learningResourceType."""
        learningresourcetype: str = value.get(
            "identifier",
            "https://w3id.org/kim/hcrt/course",
        )
        record.append_learningresourcetype(learningresourcetype)

    def convert_expires(self, value: list[str], record: LOMMetadata) -> None:
        """Convert expires."""

    def convert_trailer(self, value: dict, record: LOMMetadata) -> None:
        """Convert trailer."""

    def convert_teaches(self, value: list[dict], record: LOMMetadata) -> None:
        """Convert teaches."""

    def convert_audience(self, value: list[str], record: LOMMetadata) -> None:
        """Convert audience."""

    def convert_educationalLevel(self, value: list[dict], record: LOMMetadata) -> None:
        """Convert educationallevel."""

    def convert_keywords(self, value: list[str], record: LOMMetadata) -> None:
        """Convert keywords."""

    def convert_contentLocation(self, value: dict, record: LOMMetadata) -> None:
        """Convert contentlocation."""

    def convert_offer(self, value: list, record: LOMMetadata) -> None:
        """Convert offer."""

    def convert_numberOfCredits(self, value: list, record: LOMMetadata) -> None:
        """Convert numberOfCredits."""

    def convert_educationalCredentialsAwarded(
        self,
        value: list[str],
        record: LOMMetadata,
    ) -> None:
        """Convert educationalCredentialsAwarded."""

    def convert_competencyRequired(
        self,
        value: list[dict],
        record: LOMMetadata,
    ) -> None:
        """Convert competencyRequired."""

    def convert_applicationStartDate(self, value: str, record: LOMMetadata) -> None:
        """Convert applicationStartDate."""

    def convert_applicationDeadline(self, value: str, record: LOMMetadata) -> None:
        """Convert applicationDeadline."""

    def convert_accessMode(self, value: list[str], record: LOMMetadata) -> None:
        """Convert accessMode."""

    def convert_repeatFrequency(self, value: list[dict], record: LOMMetadata) -> None:
        """Convert repeatFrequency."""

    def convert_dateCreated(self, value: str, record: LOMMetadata) -> None:
        """Convert dateCreated."""

    def convert_dateModified(self, value: str, record: LOMMetadata) -> None:
        """Convert dateModified."""

    def convert_hollandCode(self, value: list[str], record: LOMMetadata) -> None:
        """Convert hollandCode."""

    def convert_hasPart(self, value: list[dict], record: LOMMetadata) -> None:
        """Convert hasPart."""

    def convert_isPartOf(self, value: list[dict], record: LOMMetadata) -> None:
        """Convert isPartOf."""
