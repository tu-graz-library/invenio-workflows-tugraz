# SPDX-FileCopyrightText: 2026 Graz University of Technology.
# SPDX-License-Identifier: MIT

"""Records tasks."""

from celery import shared_task
from collections.abc import Callable
from dataclasses import dataclass
from flask import current_app

from datacite.errors import DataCiteError, DataCiteNotFoundError
from invenio_access.permissions import system_identity
from invenio_drafts_resources.records import Record
from invenio_jobs.errors import TaskExecutionPartialError
from invenio_rdm_records.records.api import RDMRecord
from invenio_rdm_records.services import RDMRecordService
from invenio_rdm_records.services.pids.providers import DataCiteClient
from invenio_records_lom.records.api import LOMRecord
from invenio_records_marc21.records.api import Marc21Record


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
    url_expected: Callable[[str], list[str]]
    statistics: TaskExecutionStatistics


record_types: list[RecordType] = [
    RecordType(
        name="Publications",
        record_api=Marc21Record,
        service_api="invenio-records-marc21",
        url_expected=lambda record_id: [
            f"{current_app.config['SITE_UI_URL']}/publications/{record_id}",  # current
        ],
        statistics=TaskExecutionStatistics(),
    ),
    RecordType(
        name="Educational Resources",
        record_api=LOMRecord,
        service_api="invenio-records-lom",
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
