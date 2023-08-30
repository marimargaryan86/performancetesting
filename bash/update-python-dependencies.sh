#!/usr/bin/env bash
set -eu
ROOT_DIR="$(CDPATH='' cd -- "$(dirname -- "$0")/.." && pwd)"

pants run "${ROOT_DIR}/python/snowfall/script/bump_python_dependencies.py" -- "${ROOT_DIR}/vendor/requirements.txt" "${ROOT_DIR}/vendor/constraints.txt"

if [[ -n "$(git status --porcelain)" ]]; then
	pants generate-lockfiles --resolve=python-default
fi
