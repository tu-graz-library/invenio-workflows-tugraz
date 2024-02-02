# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 Graz University of Technology.
#
# invenio-workflows-tugraz is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.


"""Decorator functions for theses views."""

from collections.abc import Callable
from functools import wraps
from typing import Any

from flask import abort, g
from invenio_pidstore.errors import PIDDoesNotExistError
from invenio_records_marc21.proxies import current_records_marc21
from invenio_search import RecordsSearch
from invenio_search.engine import dsl
from sqlalchemy.exc import NoResultFound


def pass_record_from_pid(f: Callable) -> Callable:
    """Decorate a view to pass the record from a pid."""

    @wraps(f)
    def view(*_: dict, **kwargs: dict) -> Any:  # noqa: ANN401
        pid_value = kwargs.get("pid_value")

        search = RecordsSearch(index="marc21records")
        query = {
            "filter": [
                {"match_all": {}},
                {"match_phrase": {"metadata.fields.995.subfields.a": pid_value}},
                {"match_phrase": {"metadata.fields.995.subfields.i": "TUGRAZonline"}},
            ],
        }

        search.query = dsl.Q("bool", **query)
        search = search.params(size=1)
        result = search.execute()
        if len(result["hits"]["hits"]) == 0:
            abort(423)
        hits = result["hits"]["hits"][0]["_source"]
        hits = hits.to_dict()

        try:
            record = current_records_marc21.records_service.read_draft(
                id_=hits["id"],
                identity=g.identity,
            )
        except (PIDDoesNotExistError, NoResultFound):
            record = current_records_marc21.records_service.read(
                id_=hits["id"],
                identity=g.identity,
            )

        kwargs["record"] = record.to_dict()
        return f(**kwargs)

    return view
