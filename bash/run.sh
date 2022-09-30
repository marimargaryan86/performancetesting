#!/usr/bin/env bash
# DESCRIPTION:
#   Runs a service using pants while passing the environment variables
#   defined in .env or .env.dist where the service resides.
#
# EXAMPLE USAGE:
#   bash bash/run.sh python/snowfall/project/junction/service/client_api/main.py http
set -eu

DIR=$(dirname "${1}")
ENV_STR="PANTS_CONCURRENT=True"

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
	done <"${DIR}/.env.dist"
fi

env -S "${ENV_STR}" ./pants run "${1}:main" -- "${@:2}"
