# SPDX-FileCopyrightText: 2024-2026 Graz University of Technology.
# SPDX-License-Identifier: MIT

"""Module tests imoox."""

from collections.abc import Callable
from json import load
from pathlib import Path

import decorator
import pytest
from invenio_records_lom.utils import LOMMetadata

from invenio_workflows_tugraz.imoox.visitor import IMOOXToLOM


def load_as_json(func: Callable) -> any:
    """Decorat."""

    def wrapper(*args: dict, **__: dict) -> any:
        parent = Path(__file__).parent
        with Path(f"{parent}/data/{args[1]}.json").open() as fp:
            test = load(fp)
        with Path(f"{parent}/data/{args[1]}.json").open() as fp:
            expected = load(fp)
        return func(test, expected)

    return decorator.decorator(wrapper, func)


@pytest.mark.parametrize(
    ("test", "expected"),
    [],
)
@load_as_json
def test_visit(test: dict, expected: dict) -> None:
    """Test visit."""
    record = LOMMetadata
    visitor = IMOOXToLOM()

    visitor.visit(test, record)

    assert record.json == expected
