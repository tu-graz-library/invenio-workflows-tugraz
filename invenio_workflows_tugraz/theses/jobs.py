# SPDX-FileCopyrightText: 2025-2026 Graz University of Technology.
# SPDX-License-Identifier: MIT

"""Theses jobs."""

from invenio_jobs.jobs import JobType

from .tasks import status_arch, status_pub


class StatusArchJob(JobType):
    """Status arch job."""

    id = "status_arch"
    title = "Update Status Archive in Campusonline"
    description = "Update the status 'archive' in campusonline."

    task = status_arch


class StatusPubJob(JobType):
    """Status publication job."""

    id = "status_pub"
    title = "Update Status Publication in Campusonline"
    description = "Update the status 'publication' in campusonline."

    task = status_pub
