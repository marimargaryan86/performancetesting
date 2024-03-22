#!/usr/bin/env bash
set -eu
ROOT_DIR="$(CDPATH='' cd -- "$(dirname -- "$0")/.." && pwd)"

if [ -n "${ALLOW_BREAKING+x}" ]; then
	additional_unpin_args=("--allow-breaking")
else
	additional_unpin_args=()
fi

pants run "${ROOT_DIR}/python/snowfall/script/python_dependencies.py" -- unpin "${ROOT_DIR}/vendor/requirements.txt" "${additional_unpin_args[@]}"
pants generate-lockfiles --resolve=python-default
pants run "${ROOT_DIR}/python/snowfall/script/python_dependencies.py" -- pin "${ROOT_DIR}/vendor/requirements.txt" "${ROOT_DIR}/vendor/constraints.txt"
pants generate-lockfiles --resolve=python-default
