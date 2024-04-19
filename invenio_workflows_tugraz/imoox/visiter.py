# -*- coding: utf-8 -*-
#
# Copyright (C) 2022-2024 Graz University of Technology.
#
# invenio-workflows-tugraz is free software; you can redistribute it
# and/or modify it under the terms of the MIT License; see LICENSE
# file for more details.

"""Converter Module to facilitate conversion of metadata."""

from collections.abc import Callable
from functools import wraps
from typing import TypeVar

T = TypeVar("T")


def langstring(value: str, language: str = "x-none") -> dict:
    """Langstring."""
    return {
        "langstring": {
            "lang": language,
            "#text": value,
        },
    }


def ensure_value_str_not_empty(func: Callable[..., T]) -> Callable:
    """Decorat, only entry function if string not empty."""

    @wraps(func)
    def wrapper(*args: dict, **kwargs: dict) -> T:
        if len(args[1]) == 0:
            return False
        return func(*args, **kwargs)

    return wrapper


def ensure_value_str(func: Callable[..., T]) -> Callable:
    """Decorat, to check that value is a string."""

    @wraps(func)
    def wrapper(*args: dict, **kwargs: dict) -> T:
        if not isinstance(args[1], str):
            return False
        return func(*args, **kwargs)

    return wrapper


def ensure_value_list(list_type: str | dict | None = None) -> Callable:
    """Decorat, to check that value is a list."""

    def not_all_str(values: list) -> bool:
        return not all(isinstance(v, str) for v in values)

    def not_all_dict(values: list) -> bool:
        return not all(
            isinstance(v, dict) and (key in v for key in list_type) for v in values
        )

    def decorator(func: Callable[..., T]) -> Callable:
        @wraps(func)
        def wrapper(*args: dict, **kwargs: dict) -> T:
            if isinstance(list_type, str) and not_all_str(args[1]):
                return False
            if isinstance(list_type, dict) and not_all_dict(args[1]):
                return False

            return func(*args, **kwargs)

        return wrapper

    return decorator


def ensure_attribute_list(query: str) -> Callable:
    """Decorat, to ensure that the attribute list exists."""
    prop, base, sub = query.split(".")

    def decorator(func: Callable[..., T]) -> Callable:
        @wraps(func)
        def wrapper(*args: dict, **kwargs: dict) -> T:
            obj = getattr(args[0], prop)
            if base not in obj:
                obj[base] = {}
            if sub not in obj[base]:
                obj[base][sub] = []

            return func(*args, **kwargs)

        return wrapper

    return decorator


class Converter:
    """Converter base class."""

    def convert(self, parent: dict) -> None:
        """Convert method."""
        for attribute, value in parent.items():
            self.process(attribute, value)

    def process(self, attribute: str, value: T) -> None:
        """Execute the corresponding method to the attribute."""

        def func_not_found(*_: dict, **__: dict) -> None:
            msg = f"NO convert method for {attribute}"
            raise ValueError(msg)

        convert_func = getattr(self, f"convert_{attribute}", func_not_found)
        return convert_func(value)


class MoocToLOM(Converter):
    """Convert class to convert Mooc to LOM."""

    def __init__(self) -> None:
        """Construct MoocToLOM."""
        self.reset()
        self.language = ""

    def reset(self) -> None:
        """Reset the record structure."""
        self.record = {
            "general": {},
            "lifeCycle": {},
            "custom": {},
            "metametadata": {},
            "technical": {},
            "rights": {},
            "educational": {},
            "classification": [],
        }

    def set_language(self, parent: dict) -> None:
        """Set default language for langstring."""
        if "languages" not in parent["attributes"]:
            return

        if len(parent["attributes"]["languages"]) == 0:
            return

        self.language = parent["attributes"]["languages"][0]

    def convert(self, parent: dict) -> None:
        """Convert overrides base convert method to return the record."""
        self.reset()
        self.set_language(parent)

        super().convert(parent)
        return self.record

    @ensure_attribute_list("record.general.identifier")
    def convert_id(self, value: str) -> None:
        """Convert id attribute."""
        self.record["general"]["identifier"].append(
            {
                "catalog": "imoox",
                "entry": langstring(value),
            },
        )

    def convert_type(self, value: str) -> None:
        """Convert type attribute."""

    def convert_attributes(self, value: dict) -> None:
        """Convert attributes attribute."""
        super().convert(value)

    @ensure_value_str
    def convert_name(self, value: str) -> None:
        """Convert name attribute."""
        self.record["general"]["title"] = langstring(value, self.language)

    def convert_courseCode(self, value: dict) -> None:
        """Convert courseCode attribute."""

    def convert_courseMode(self, value: dict) -> None:
        """Convert courseMode attribute."""

    @ensure_value_str
    @ensure_value_str_not_empty
    @ensure_attribute_list("record.general.description")
    def convert_abstract(self, value: str) -> None:
        """Convert abstract attribute."""
        self.record["general"]["description"].append(langstring(value, self.language))

    @ensure_value_str
    @ensure_value_str_not_empty
    @ensure_attribute_list("record.general.description")
    def convert_description(self, value: str) -> None:
        """Convert description attribute."""
        self.record["general"]["description"].append(langstring(value, self.language))

    @ensure_value_list(str)
    def convert_languages(self, value: str) -> None:
        """Convert languages attribute."""
        self.record["general"]["language"] = value

    def convert_startDate(self, value: str) -> None:
        """Convert startDate attribute."""
        self.record["lifeCycle"]["datetime"] = value.split("T")[0]

    def convert_availableUntil(self, value: str) -> None:
        """Convert availableUntil attribute."""

    def convert_endDate(self, value: str) -> None:
        """Convert endDate attribute."""

    def convert_image(self, value: str) -> None:
        """Convert image attribute."""
        self.record["technical"]["thumbnail"] = value

    def convert_video(self, value: str) -> None:
        """Convert video attribute."""

    @ensure_value_list({"name": str, "description": str})
    @ensure_attribute_list("record.lifeCycle.contribute")
    def convert_instructors(self, value: str) -> None:
        """Convert instructors attribute."""
        for instructor in value:
            self.record["lifeCycle"]["contribute"].append(
                {
                    "role": {
                        "source": langstring("LOMv1.0"),
                        "value": langstring("Author"),
                    },
                    "entity": instructor["name"],
                    "description": langstring(instructor["description"], self.language),
                },
            )

    @ensure_value_list()
    @ensure_attribute_list("record.educational.description")
    def convert_learningobjectives(self, value: str) -> None:
        """Convert learningobjectives attribute."""
        for desc in value:
            self.record["educational"]["description"].append(
                langstring(desc, self.language),
            )

    def convert_duration(self, value: str) -> None:
        """Convert duration attribute."""
        self.record["technical"]["duration"] = {"description": langstring(value)}

    @ensure_value_list({"name": str})
    @ensure_attribute_list("record.metametadata.contribute")
    def convert_partnerInstitute(self, value: list[dict]) -> None:
        """Convert partnerInstitute attribute."""
        for partner in value:
            self.record["lifeCycle"]["contribute"].append(
                {
                    "role": {
                        "source": langstring("LOMv1.0"),
                        "value": langstring("Publisher"),
                    },
                    "entity": partner["name"],
                },
            )

    @ensure_attribute_list("record.metametadata.contribute")
    def convert_moocProvider(self, value: dict) -> None:
        """Convert moocProvider attribute."""
        self.record["metametadata"]["contribute"].append(
            {
                "role": {
                    "source": langstring("LOMv1.0"),
                    "value": langstring("Provider"),
                },
                "entity": value["name"],  # ,
                # "url": value["url"],
                # "logo": value["logo"],
            },
        )

    def convert_url(self, value: str) -> None:
        """Convert url attribute."""
        self.record["technical"]["location"] = {"type": "URI", "#text": value}

    def convert_workload(self, value: str) -> None:
        """Convert workload attribute."""
        self.record["educational"]["typicalLearningTime"] = {
            "duration": {
                "datetime": value,
                "description": "workload",
            },
        }

    def convert_courseLicenses(self, value: list) -> None:
        """Convert courseLicenses attribute."""
        self.record["rights"] = {
            "copyrightandotherrestrictions": {
                "source": langstring("LOMv1.0"),
                "value": langstring("yes"),
            },
            "url": value[0]["url"],
            "description": langstring(value[0]["url"], "x-t-cc-url"),
        }

    def convert_access(self, value: dict) -> None:
        """Convert access attribute."""

    def convert_categories(self, value: dict) -> None:
        """Convert categories attribute."""
        super().convert(value)

    def convert_oefos(self, value: dict) -> None:
        """Convert oefos attribute."""
        taxon = [
            {
                "id": f"https://w3id.org/oerbase/vocabs/oefos2012/{o['identifier']}",
                "entry": [langstring(o["name"], "de")],
            }
            for o in value
        ]
        self.record["classification"].append(
            {
                "purpose": {
                    "source": langstring("LOMv1.0"),
                    "value": langstring("discipline"),
                },
                "taxonpath": {
                    "source": langstring(
                        "https://w3id.org/oerbase/vocabs/oefos2012",
                        "x-t-oefos",
                    ),
                    "taxon": taxon,
                },
            },
        )
