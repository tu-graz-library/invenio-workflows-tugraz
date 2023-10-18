# -*- coding: utf-8 -*-
#
# Copyright (C) 2024 Graz University of Technology.
#
# invenio-workflows-tugraz is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Module test oer."""

from json import load
from pathlib import Path

import decorator
import pytest
from invenio_records_marc21 import Marc21Metadata

from invenio_workflows_tugraz.oer.convert import LOM2Marc21


def load_as_json(func: callable) -> any:
    """Decorat to load content of file as dictionary from a json file."""

    def wrapper(*args: dict, **__: dict) -> any:
        parent = Path(__file__).parent
        with Path(f"{parent}/data/{args[1]}.json").open() as fp:
            test = load(fp)
        with Path(f"{parent}/data/{args[2]}.json").open() as fp:
            expected = load(fp)
        return func(test, expected)

    return decorator.decorator(wrapper, func)


@pytest.mark.parametrize(
    ("test", "expected"),
    [
        ("empty_test", "empty_expected"),
    ],
)
@load_as_json
def test_convert(test: dict, expected: dict) -> None:
    """Test convert."""
    record = Marc21Metadata()
    visitor = LOM2Marc21(record)

    visitor.visit(test, record)

    assert record.json == expected
