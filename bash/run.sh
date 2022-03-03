#!/usr/bin/env bash
# DESCRIPTION:
#   Runs a service using pants while passing the environment variables
#   defined in .env or .env.dist where the service resides.
#
# EXAMPLE USAGE:
#   bash bash/run.sh python/snowfall/junction/client_api/main.py
#   bash bash/run.sh python/snowfall/junction/gtfs_feed/main.py import
set -eu

DIR=$(dirname "${1}")
ENV_STR=""

if [ -f "${DIR}/.env" ]; then
	ENV_STR=$(xargs -0 <"${DIR}/.env")
elif [ -f "${DIR}/.env.dist" ]; then
	ENV_STR=$(xargs -0 <"${DIR}/.env.dist")
fi

ENV_STR="${ENV_STR} PANTS_CONCURRENT=True"

# shellcheck disable=SC2086
env $ENV_STR ./pants run "${1}" -- "${@:2}"
