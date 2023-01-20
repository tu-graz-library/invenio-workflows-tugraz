# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Graz University of Technology.
#
# invenio-workflows-tugraz is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Theses Workflows."""

from typing import Callable
from xml.etree.ElementTree import Element

from invenio_campusonline.types import (
    CampusOnlineConfigs,
    CampusOnlineID,
    ThesesFilter,
    ThesesState,
)
from invenio_config_tugraz import get_identity_from_user_by_email
from invenio_records_marc21 import (
    DuplicateRecordError,
    Marc21Metadata,
    check_about_duplicate,
    create_record,
    current_records_marc21,
)
from invenio_search import RecordsSearch
from invenio_search.engine import dsl

from .convert import CampusOnlineToMarc21
from .types import CampusOnlineId


@check_about_duplicate.register
def _(value: CampusOnlineId):
    """Check about double campus online id."""
    check_about_duplicate(str(value), value.category)


def cms_id(record):
    """CMS id."""
    return record["_source"]["metadata"]["fields"]["995"][0]["subfields"]["d"][0]


def marc_id(record):
    """Marc id."""
    return record["_source"]["id"]


def theses_filter_for_locked_records():
    """This function returns a tuple.

    FILTER: xml filter to get locked records
    STATE: [open, locked]
    return ThesesFilter
    """
    filter_ = [
        """<bas:thesesType>ALL</bas:thesesType>""",
        """<bas:state name="LOCKED" negate="false"><bas:from>2022-01-01T00:01:00+00:00</bas:from></bas:state>""",
    ]
    state = ThesesState.LOCKED
    return ThesesFilter(filter_, state)


def theses_filter_for_open_records():
    """This function returns a list of tuples.

    FILTER: xml filter to get open records
    STATE: [open, locked]
    return ThesesFilter
    """
    filter_ = [
        """<bas:thesesType>ALL</bas:thesesType>""",
        """<bas:state name="IFG" negate="false"><bas:from>2022-01-01T00:01:00+00:00</bas:from></bas:state>""",
    ]
    state = ThesesState.OPEN
    return ThesesFilter(filter_, state)


def theses_create_aggregator():
    """This function returns a list of marc21 ids."""
    search = RecordsSearch(index="marc21records-drafts")
    query = {
        "must_not": [
            {
                "exists": {
                    "field": "metadata.fields.001",
                },
            }
        ],
        "must": [
            {
                "exists": {
                    "field": "metadata.fields.995",
                },
            }
        ],
    }

    search.query = dsl.Q("bool", **query)
    search = search.params(size=50000)
    result = search.execute()
    hits = result["hits"]["hits"]
    return [(marc_id(record), cms_id(record)) for record in hits]


def theses_update_aggregator():
    """This function returns a list of tuple(marc21, cms_id)."""
    search = RecordsSearch(index="marc21records-draft")
    query = {
        "must_not": [
            {
                "exists": {
                    "field": "metadata.fields.001",
                },
            }
        ]
    }
    search.query = dsl.Q("bool", **query)
    result = search.execute()
    hits = result["hits"]["hits"]
    return [(marc_id(record), cms_id(record)) for record in hits]


def exists_fulltext(thesis: Element) -> bool:
    """Check against fulltext existens."""
    ns = "http://www.campusonline.at/thesisservice/basetypes"
    xpath = f".//{{{ns}}}attr[@key='VOLLTEXT']"
    ele = thesis.find(xpath)

    if ele is None:
        return False
    elif ele.text == "N":
        return False
    else:
        return True


def import_func(
    cms_id: CampusOnlineID,
    configs: CampusOnlineConfigs,
    get_metadata: Callable,
    download_file: Callable,
):
    """This is the function to import the record into the repository."""
    try:
        check_about_duplicate(CampusOnlineId(cms_id))
    except DuplicateRecordError:
        return

    thesis = get_metadata(configs.endpoint, configs.token, cms_id)

    if not exists_fulltext(thesis):
        raise RuntimeError("record has no associated file")

    file_path = download_file(configs.endpoint, configs.token, cms_id)

    marc21_record = Marc21Metadata()
    convert = CampusOnlineToMarc21(marc21_record)

    convert.visit(thesis, marc21_record)

    identity = get_identity_from_user_by_email(email=configs.user_email)
    service = current_records_marc21.records_service
    data = marc21_record.json
    data["access"] = {
        "record": "restricted",
        "files": "restricted",
    }

    return create_record(service, data, [file_path], identity, do_publish=False)
