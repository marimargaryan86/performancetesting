#!/usr/bin/env bash
set -eu
ROOT_DIR="$(CDPATH='' cd -- "$(dirname -- "$0")/.." && pwd)"

pants run "${ROOT_DIR}python/snowfall/script/python_dependencies.py" -- unpin "${ROOT_DIR}vendor/requirements.txt"
pants generate-lockfiles --resolve=python-default
pants run "${ROOT_DIR}python/snowfall/script/python_dependencies.py" -- pin "${ROOT_DIR}vendor/requirements.txt" "${ROOT_DIR}vendor/constraints.txt"
