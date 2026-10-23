#!/usr/bin/env bash
# SPDX-FileCopyrightText: 2022-2026 Graz University of Technology.
# SPDX-License-Identifier: MIT

# Quit on errors
set -o errexit

# Quit on unbound symbols
set -o nounset

# Always bring down docker services
function cleanup() {
    eval "$(docker-services-cli down --env)"
}

# Check for arguments
# Note: "-k" would clash with "pytest"
keep_services=0
pytest_args=()
for arg in $@; do
  # from the CLI args, filter out some known values and forward the rest to "pytest"
  # note: we don't use "getopts" here b/c of some limitations (e.g. long options),
  #       which means that we can't combine short options (e.g. "./run-tests -Kk pattern")
  case ${arg} in
    -K|--keep-services)
      keep_services=1
      ;;
    *)
      pytest_args+=( ${arg} )
      ;;
  esac
done

if [[ ${keep_services} -eq 0 ]]; then
  trap cleanup EXIT
fi

ruff check .

eval "$(docker-services-cli up --db ${DB:-postgresql} --search ${SEARCH:-opensearch} --env)"
python -m pytest ${pytest_args[@]+"${pytest_args[@]}"}
