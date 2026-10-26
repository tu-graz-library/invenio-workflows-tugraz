#!/usr/bin/env bash
# SPDX-FileCopyrightText: 2022-2026 Graz University of Technology.
# SPDX-License-Identifier: MIT

# Quit on errors
set -o errexit

# Quit on unbound symbols
set -o nounset

ruff check .

eval "$(docker-services-cli up --db ${DB:-postgresql} --search ${SEARCH:-opensearch} --env)"
python -m pytest
