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
from invenio_records_marc21 import Marc21Metadata, create_record, current_records_marc21

from .convert import CampusOnlineToMarc21


def theses_filter_for_locked_records():
    """This function returns a tuple.
    FILTER: xml filter to get locked records
    STATE: [open, locked]
    return ThesesFilter"""

    filter_ = [
        """<bas:thesesType>ALL</bas:thesesType>""",
        """<bas:state name="LOCKED" negate="false"></bas:state>""",
    ]
    state = ThesesState.LOCKED
    return ThesesFilter(filter_, state)


def theses_filter_for_open_records():
    """This function returns a list of tuples.
    FILTER: xml filter to get open records
    STATE: [open, locked]
    return ThesesFilter"""
    filter_ = [
        """<bas:thesesType>ALL</bas:thesesType>""",
        """<bas:state name="IFG" negate="false"></bas:state>""",
    ]
    state = ThesesState.OPEN
    return ThesesFilter(filter_, state)


def exists_fulltext(thesis: Element) -> bool:
    """check against fulltext existens."""
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
    print("----------------------import_func--------------------------------------")
    thesis = get_metadata(configs.endpoint, configs.token, cms_id)

    if not exists_fulltext(thesis):
        raise RuntimeError("record has no accosiated file")

    file_path = download_file(configs.endpoint, configs.token, cms_id)

    convert = CampusOnlineToMarc21()
    marc21_record = Marc21Metadata()

    convert.visit(thesis, marc21_record)

    identity = get_identity_from_user_by_email(email=configs.user_email)
    service = current_records_marc21.records_service
    record = create_record(service, marc21_record, file_path, identity)

    # TODO: set access of record
    # if cms.state == ThesesState.LOCKED
    #   set file permission to restricted
    # elif cms.state == ThesesState.OPEN
    #   set file permission to public

    return record
