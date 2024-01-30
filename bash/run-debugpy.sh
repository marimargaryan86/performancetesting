#!/usr/bin/env bash
# DESCRIPTION:
#   Runs a service using debugpy while passing the environment variables
#   defined in .env or .env.dist where the service resides.
set -eu

DIR=$(dirname "${3}")
ENV_STR="PYTHONUNBUFFERED=1 PYDEVD_DISABLE_FILE_VALIDATION=1 PANTS_CONCURRENT=TRUE"

if [ -f "${DIR}/.env" ]; then
	ENV_FILE="${DIR}/.env"
elif [ -f "${DIR}/.env.dist" ]; then
	ENV_FILE="${DIR}/.env.dist"
fi

if [ -n "${ENV_FILE+x}" ]; then
	while read -r line; do
		key="${line%%=*}"
		value="${line#*=}"
		ENV_STR="${ENV_STR} ${key@Q}=${value@Q}"
	done <"${ENV_FILE}"
fi

env -S "${ENV_STR}" "${1}" -m debugpy --listen "${2}" --wait-for-client -m "${4}" "${5}"
