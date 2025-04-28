# -*- coding: utf-8 -*-
#
# Copyright (C) 2025 Graz University of Technology.
#
# invenio-workflows-tugraz is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

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
