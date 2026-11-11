# SPDX-FileCopyrightText: 2026 Graz University of Technology.
# SPDX-License-Identifier: MIT

"""Records tasks."""

from celery import shared_task
from collections.abc import Callable
from dataclasses import dataclass
from deepdiff import DeepDiff
from flask import current_app
from flask_resources.serializers import MarshmallowSerializer

from datacite.errors import DataCiteError, DataCiteNotFoundError
from invenio_access.permissions import system_identity
from invenio_drafts_resources.records import Record
from invenio_jobs.errors import TaskExecutionPartialError
from invenio_rdm_records.records.api import RDMRecord
from invenio_rdm_records.resources.serializers import DataCite43JSONSerializer
from invenio_rdm_records.services import RDMRecordService
from invenio_rdm_records.services.pids.providers import DataCiteClient
from invenio_records_lom.records.api import LOMRecord
from invenio_records_lom.resources.serializers import LOMToDataCite44Serializer
from invenio_records_marc21.records.api import Marc21Record
from invenio_records_marc21.resources.serializers import Marc21DataCite43JSONSerializer


class TaskExecutionStatistics:
    """Class to hold statistics for task execution."""

    def __init__(self) -> None:
        """Initialize statistics."""
        self.stat: dict[str, int | list[str]] = {
            "total number": 0,
            "a DOI": 0,
            "DOI with wrong URL": 0,
            "DOI with fixed URL": 0,
            "DOI REST API errors": 0,
            "restricted access (skipped)": 0,
            "DOI republished": 0,
            "differing metadata": 0,
            "diff: dictionary_item_removed": 0,
        }

    def increment(self, base_key: str, item: str | None = None) -> None:
        """Increment counter and store item in list if present."""
        self.stat[base_key] += 1
        if item:
            if (list_key := base_key + " - record list") not in self.stat:
                self.stat[list_key]: list[str] = []
            self.stat[list_key].append(item)

    def accumulate(self, other: dict) -> None:
        """Accumulate statistics from another instance."""
        for key in self.stat:
            self.stat[key] += other.get(key, 0)

    def failure(self) -> bool:
        """Get failure state."""
        return self.stat["DOI with wrong URL"] + self.stat["DOI REST API errors"] > 0

    def summary(self, record_type_name: str) -> str:
        """Return the statistics as a string.

        Ignore items with value 0.
        """
        msg = ""
        for key, value in self.stat.items():
            if (isinstance(value, int) and value > 0) or isinstance(value, list):
                msg += f"{record_type_name} records with {key}: {value}\n"
        return msg

    def log(self, record_type_name: str) -> None:
        """Log statistics summary."""
        current_app.logger.info("Summary for %s:", record_type_name)
        for line in self.summary(record_type_name).splitlines():
            current_app.logger.info("%s", line)

    def reset(self) -> None:
        """Reset the statistics counter and lists."""
        for key, value in list(self.stat.items()):
            if isinstance(value, int):
                self.stat[key] = 0
            elif isinstance(value, list):
                self.stat.pop(key, None)


CURRENT_EXPECTED_URL = 0


@dataclass
class RecordType:
    """Class to hold all data required to run url-reconciliation for a given record type."""

    name: str
    record_api: type[Record]
    service_api: str
    serializer: type[MarshmallowSerializer]
    url_expected: Callable[[str], list[str]]
    statistics: TaskExecutionStatistics


record_types: list[RecordType] = [
    RecordType(
        name="Publications",
        record_api=Marc21Record,
        service_api="invenio-records-marc21",
        serializer=Marc21DataCite43JSONSerializer,
        url_expected=lambda record_id: [
            f"{current_app.config['SITE_UI_URL']}/publications/{record_id}",  # current
        ],
        statistics=TaskExecutionStatistics(),
    ),
    RecordType(
        name="Educational Resources",
        record_api=LOMRecord,
        service_api="invenio-records-lom",
        serializer=LOMToDataCite44Serializer,
        url_expected=lambda record_id: [
            f"{current_app.config['SITE_UI_URL']}/oer/{record_id}",  # current
            f"{current_app.config['SITE_UI_URL']}/oer/doi/{current_app.config['DATACITE_PREFIX']}/{record_id}",  # legacy
        ],
        statistics=TaskExecutionStatistics(),
    ),
    RecordType(
        name="Research Results",
        record_api=RDMRecord,
        service_api="invenio-rdm-records",
        serializer=DataCite43JSONSerializer,
        url_expected=lambda record_id: [
            f"{current_app.config['SITE_UI_URL']}/doi/{current_app.config['DATACITE_PREFIX']}/{record_id}",  # current
            f"{current_app.config['SITE_UI_URL']}/records/{record_id}",  # legacy
        ],
        statistics=TaskExecutionStatistics(),
    ),
]


def restricted_access_record(record: Record) -> bool:
    """Check whether the record is tagged as restricted / embargoed."""
    is_restricted = record.data.get("access", {}).get("record", "") == "restricted"
    is_embargoed = record.data.get("access", {}).get("embargo", "").get("active", False)
    return is_restricted or is_embargoed


def query_url(
    record: Record,
    client: DataCiteClient,
    service: RDMRecordService,
    statistics: TaskExecutionStatistics,
) -> str | None:
    """Query the records url stored in datacite metadata."""
    record_id = record.data.get("id", None)
    record_doi = record.data.get("pids", {}).get("doi", {}).get("identifier", None)

    url_query = None
    try:
        url_query = client.api.get_doi(record_doi)
    except DataCiteNotFoundError:
        service.pids.register_or_update(
            id_=record_id,
            identity=system_identity,
            scheme="doi",
        )
        statistics.increment(base_key="DOI republished", item=record_id)
    except DataCiteError:
        statistics.increment(base_key="DOI REST API errors", item=record_id)

    return url_query


def reconcile_url(
    record: Record,
    url_query: str,
    urls_expected: list[str],
    client: DataCiteClient,
    statistics: TaskExecutionStatistics,
) -> None:
    """Check whether the records url is correctly stored in the datacite metadata.

    If not, update metadata with correct url.
    """
    record_id = record.data.get("id", None)
    record_doi = record.data.get("pids", {}).get("doi", {}).get("identifier", None)

    if url_query not in urls_expected:
        url_query = client.api.update_url(
            record_doi,
            urls_expected[CURRENT_EXPECTED_URL],
        )
        if url_query == urls_expected[CURRENT_EXPECTED_URL]:
            statistics.increment(base_key="DOI with fixed URL", item=record_id)
        else:
            statistics.increment(base_key="DOI with wrong URL", item=record_id)


@shared_task
def reconcile_records_dois() -> None:
    """Check URLs stored in DataCite for all records with a DOI."""
    client = DataCiteClient("datacite")  # -> DataCiteRESTClient

    statistics_total = TaskExecutionStatistics()

    for record_type in record_types:
        records = record_type.record_api.model_cls.query.all()

        statistics = record_type.statistics
        statistics.stat["total number"] = len(records)

        for record in records:
            record_id = record.data.get("id", None)
            record_doi = (
                record.data.get("pids", {}).get("doi", {}).get("identifier", None)
            )

            if record_doi is None or record_doi == "":
                continue
            statistics.increment(base_key="a DOI")

            if restricted_access_record(record):
                statistics.increment(base_key="restricted access (skipped)")
                continue

            if (
                url_query := query_url(
                    record=record,
                    client=client,
                    service=current_app.extensions[
                        record_type.service_api
                    ].records_service,
                    statistics=statistics,
                )
            ) is None:
                continue

            reconcile_url(
                record=record,
                url_query=url_query,
                urls_expected=record_type.url_expected(record_id),
                client=client,
                statistics=statistics,
            )

        statistics.log(record_type.name)
        statistics_total.accumulate(statistics.stat)
        statistics.reset()

    if statistics_total.failure():
        raise TaskExecutionPartialError(statistics_total.summary("Overall"))


def query_metadata(
    record: Record,
    client: DataCiteClient,
    statistics: TaskExecutionStatistics,
) -> dict | None:
    """Query the records metadata stored in datacite."""
    record_id = record.data.get("id", None)
    record_doi = record.data.get("pids", {}).get("doi", {}).get("identifier", None)

    query_params = "?affiliation=true"

    json_query = None
    try:
        json_query = client.api.get_metadata(record_doi + query_params)
    except DataCiteError:
        statistics.increment(base_key="DOI REST API errors", item=record_id)

    return json_query


def compare_metadata(
    ours: dict,
    theirs: dict,
    statistics: TaskExecutionStatistics,
) -> bool:
    """Compare the records metadata stored in repository ('ours') and DataCite ('theirs').

    Consider only those DataCite MetaData Properties in DeepDiff-argument 'include_paths'
    that can actually be supplied for a DOI.
    The two provided dictionaries contain usually more entries than those.

    The DeepDiff return value is a dictionary itself that can contains following keys:
    - type_changes:
        - root['publicationYear'] will always be present here, because 'ours' will hold the
          publication year as a string in the serialized record, and datacite will always
          return an int here -> to check for a difference compare the (casted) values,
          the presence of type changes alone does not mean that there are difference.
    - dictionary_item_added:
        - 'theirs' always holds all keys. The additional keys can be ignored, because their
          absence in 'ours' means, that there are no metadata available in the record
          that could be matched to these properties.
    - dictionary_item_removed:
        - Missing keys mean 'ours' holds metadata properties that aren't datacite metadata
          properties. There may be following reasons:
            1) Coding error on our side (e.g. misspelling of a property-name),
          but more likely:
            2) the DataCite metadata schema changed
        - Removed items will be ignored in the diff, but to raise awareness, this incidence
          will be logged.
    - values_changed:
        - Indicates that the metadata differ.
    - iterable_item_removed:
        - Indicates that the metadata differ.
    - ... there may be further, but these are unrelated to the current use case.

    General considerations:
    As soon as there is a single difference metadata differ.
    The actual difference in the values does not matter.
    """
    diff = DeepDiff(
        t1=ours,
        t2=theirs,
        include_paths=[
            "root['types']",
            "root['titles']",
            "root['creators']",
            "root['publisher']",
            "root['publicationYear']",
            "root['schemaVersion']",
            "root['subjects']",
            "root['contributors']",
            "root['language']",
            "root['dates']",
            "root['alternateIdentifiers']",
            "root['relatedIdentifiers']",
            "root['rightsList']",
            "root['descriptions']",
            "root['geoLocations']",
            "root['relatedItems']",
            "root['sizes']",
            "root['formats']",
            "root['fundingReferences']",
        ],
        ignore_order=True,
        verbose_level=2,
    )

    # log if some of the above keys have been removed in 'theirs':
    if "dictionary_item_removed" in diff:
        statistics.increment(base_key="diff: dictionary_item_removed")

    # values of type string changed:
    if "values_changed" in diff:
        if "root['language']" in diff["values_changed"]:
            # datacite seems to perform some kind of mapping of language keys,
            # for example sending "eng" will be stored as "en"
            # hence check whether the first two letters match
            old_value = diff["values_changed"]["root['language']"]["old_value"]
            new_value = diff["values_changed"]["root['language']"]["new_value"]
            if old_value[:2] != new_value[:2]:
                return True

        else:
            return True

    # values of type list or dict changed:
    if "iterable_item_removed" in diff:
        return True

    # analyze the type changes:
    if "type_changes" in diff:
        for item in diff["type_changes"]:
            # In 'ours' the deepest-level value type is str.
            # example: "root['publicationYear']": {
            #                   'old_type': <class 'str'>,
            #                   'new_type': <class 'int'>,
            #                   'old_value': '2024',
            #                   'new_value': 2024}
            #                   }
            if diff["type_changes"][item]["old_value"] != str(
                diff["type_changes"][item]["new_value"],
            ):
                return True

    return False


@shared_task
def update_metadata_in_datacite() -> None:
    """Update record metadata of in DataCite, when differing to repository metadata."""
    client = DataCiteClient("datacite")

    statistics_total = TaskExecutionStatistics()

    for record_type in record_types:
        records = record_type.record_api.model_cls.query.all()

        statistics = record_type.statistics
        statistics.stat["total number"] = len(records)

        for record in records:
            record_id = record.data.get("id", None)
            record_doi = (
                record.data.get("pids", {}).get("doi", {}).get("identifier", None)
            )

            if record_doi is None or record_doi == "":
                continue
            statistics.increment(base_key="a DOI")

            if restricted_access_record(record):
                statistics.increment(base_key="restricted access (skipped)")
                continue

            # record metadata from datacite serializer
            serialized_record = record_type.serializer().dump_obj(record.json)

            # datacite metadata
            if (
                json_remote := query_metadata(
                    record=record,
                    client=client,
                    statistics=statistics,
                )
            ) is None:
                continue

            # compare and update metadata in datacite if indicated
            if compare_metadata(
                ours=serialized_record,
                theirs=json_remote,
                statistics=statistics,
            ):
                statistics.increment(base_key="differing metadata", item=record_id)
                current_app.extensions[
                    record_type.service_api
                ].records_service.pids.register_or_update(
                    id_=record_id,
                    identity=system_identity,
                    scheme="doi",
                )

        statistics.log(record_type.name)
        statistics_total.accumulate(statistics.stat)
        statistics.reset()

    if statistics_total.failure():
        raise TaskExecutionPartialError(statistics_total.summary("Overall"))
