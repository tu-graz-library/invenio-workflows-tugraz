#!/usr/bin/env bash
# -*- coding: utf-8 -*-
#
# Copyright (C) 2022-2023 Graz University of Technology.
#
# invenio-workflows-tugraz is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

# Quit on errors
set -o errexit

# Quit on unbound symbols
set -o nounset

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

# if [[ ${keep_services} -eq 0 ]]; then
#   trap cleanup EXIT
# fi


ruff .

python -m check_manifest
python -m sphinx.cmd.build -qnNW docs docs/_build/html
python -m pytest ${pytest_args[@]+"${pytest_args[@]}"}
