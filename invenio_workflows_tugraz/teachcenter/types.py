# -*- coding: utf-8 -*-
#
# Copyright (C) 2022-2024 Graz University of Technology.
#
# invenio-workflows-tugraz is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Teachcenter types."""


from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum, auto, unique
from functools import singledispatchmethod
from pathlib import Path

from invenio_records_lom.records import LOMDraft
from invenio_records_lom.utils import LOMRecordData


@dataclass(frozen=True)
class Color:
    """The class is for the output color management."""

    neutral = "white"
    error = "red"
    warning = "yellow"
    abort = "magenta"
    success = "green"
    alternate = ("blue", "cyan")


@dataclass(frozen=True)
class FileCacheInfo:
    """Holds a file-path and the file's md5-hash."""

    hash_sha1: str
    path: Path


@dataclass(frozen=True)
class Key(ABC):
    """Common ancestor to all Key classes."""

    @property
    @abstractmethod
    def resource_type(self) -> str:
        """The resource_type associated to the key, one of `LOM_RESOURCE_TYPES`."""

    @abstractmethod
    def __str__(self) -> str:
        """Convert `self` to unique string representation."""

    def __hash__(self) -> str:
        """Get hash."""
        return self.get_moodle_pid_value()

    @abstractmethod
    def get_moodle_pid_value(self) -> str:
        """Return the primary hash of Key."""


@dataclass(frozen=True)
class FileKey(Key):
    """Key for files as to disambiguate it from keys for units and courses."""

    url: str
    year: str
    semester: str
    hash_sha1: str

    resource_type = "file"

    @singledispatchmethod
    def __init__(self, url: str, year: str, semester: str, hash_sha1: str) -> None:
        """Construct."""
        # dataclass frozen is nice but needs following not handy construct
        object.__setattr__(self, "url", url)
        object.__setattr__(self, "year", year)
        object.__setattr__(self, "semester", semester)
        object.__setattr__(self, "hash_sha1", hash_sha1)

    @__init__.register
    def _(
        self,
        moodle_file_metadata: dict,
    ) -> None:
        """Create `cls` via info from moodle-json and file-cache."""
        try:
            # application profile 1.0
            url = moodle_file_metadata["fileurl"]
        except KeyError:
            # application profile 2.0
            url = moodle_file_metadata["source"]
        year = moodle_file_metadata["year"]
        semester = moodle_file_metadata["semester"]
        try:
            # application profile 1.0
            hash_sha1 = moodle_file_metadata["contenthash"]
        except KeyError:
            # application profile 2.0
            hash_sha1 = moodle_file_metadata["identifier"].split(":")[-1]
        self.__init__(url, year, semester, hash_sha1)

    def __str__(self) -> str:
        """Get string-representation."""
        url = f"url={self.url}"
        year = f"year={self.year}"
        semester = f"semester={self.semester}"
        hash_sha1 = f"hash_sha1={self.hash_sha1}"
        return f"FileKey({url}, {year}, {semester}, {hash_sha1})"

    def get_moodle_pid_value(self) -> str:
        """Get moodle pid value."""
        return self.hash_sha1


@dataclass(frozen=True)
class LinkKey(Key):
    """Key for links only records."""

    url: str

    resource_type = "link"

    @singledispatchmethod
    def __init__(self, url: str) -> None:
        """Construct."""
        object.__setattr__(self, "url", url)

    def __str__(self) -> str:
        """Get string-representation."""
        url = f"url={self.url}"
        return f"LinkKey({url})"

    def get_moodle_pid_value(self) -> str:
        """Get moodle pid value."""
        return self.url


@unique
class Status(Enum):
    """Status."""

    NEW = auto()
    EDIT = auto()


@dataclass
class BaseRecord:
    """Base."""

    key: Key
    pid: str
    data: LOMRecordData
    status: Status
    draft: LOMDraft

    @property
    def json(self) -> dict:
        """Get json."""
        return self.metadata.json


@dataclass
class FileRecord(BaseRecord):
    """File."""

    @property
    def url(self) -> str:
        """Get url."""
        return self.key.url

    @property
    def hash_sha1(self) -> str:
        """Get hash_sha1."""
        return self.key.hash_sha1


@dataclass
class LinkRecord(BaseRecord):
    """Link."""
