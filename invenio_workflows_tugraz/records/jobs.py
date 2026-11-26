# SPDX-FileCopyrightText: 2026 Graz University of Technology.
# SPDX-License-Identifier: MIT

"""Records jobs."""

from invenio_i18n import lazy_gettext as _
from invenio_jobs.jobs import JobType, PredefinedArgsSchema

from marshmallow import fields

from .tasks import reconcile_records_dois, update_metadata_in_datacite


class RecordsPredefinedArgsSchema(PredefinedArgsSchema):
    """Schema of input arguments for `ReconcileRecordsDOIsJob`."""

    job_arg_schema = fields.String(
        metadata={"type": "hidden"},
        dump_default="RecordsPredefinedArgsSchema",
        load_default="RecordsPredefinedArgsSchema",
    )


class ReconcileRecordsDOIsJob(JobType):
    """Job for reconciling URLs stored in DataCite for each record with a DOI."""

    arguments_schema = RecordsPredefinedArgsSchema
    description = _("Reconcile URLs stored in DataCite DOIs of all records.")
    id = "reconcile_records_dois"
    task = reconcile_records_dois
    title = _("Reconcile Record URLs in DataCite")


class UpdateMetadataDataCiteJob(JobType):
    """Job for updating record metadata in datacite with the ones from repository."""

    arguments_schema = RecordsPredefinedArgsSchema
    description = _("Update Record Metadata in DataCite.")
    id = "update_metadata_in_datacite"
    task = update_metadata_in_datacite
    title = _("Update Record Metadata in DataCite")
