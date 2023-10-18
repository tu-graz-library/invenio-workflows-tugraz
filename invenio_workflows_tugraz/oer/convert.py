# -*- coding: utf-8 -*-
#
# Copyright (C) 2024 Graz University of Technology.
#
# invenio-workflows-tugraz is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Convert from LOM to Marc21."""

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

    def __init__(self, record: Marc21Metadata) -> None:
        """Construct."""
        super().__init__()

        # TODO: add hardcoded categories

    def visit_general(self, value: dict, record: Marc21Metadata) -> None:
        """Process General."""
        # TODO

    def visit_title(self, value: dict, **__: dict) -> None:
        """Process ."""
        # TODO

    def visit_language(self, value: str, record: Marc21Metadata) -> None:
        """Process ."""
        # TODO

    def visit_description(self, value: list, record: Marc21Metadata) -> None:
        """Process ."""
        # TODO

    def visit_technical(self, value: dict, record: Marc21Metadata) -> None:
        """Process technical."""
        # TODO

    def visit_location(self, value: dict, record: Marc21Metadata) -> None:
        """Process location."""
        # TODO

    def visit_educational(self, value: dict, record: Marc21Metadata) -> None:
        """Process educational."""
        # TODO

    def visit_rights(self, value: dict, record: Marc21Metadata) -> None:
        """Process rights."""
        # TODO

    def visit_classification(self, value: dict, record: Marc21Metadata) -> None:
        """Process classification."""
        # TODO
