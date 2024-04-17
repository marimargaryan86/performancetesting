#!/usr/bin/env bash

set -eu

EXPECTED_SERVICE_NAME="${1}"
CURRENT_SERVICE_NAME=$(jq -r ".command.name" "${2}")
FAILURE=0

if [[ "${EXPECTED_SERVICE_NAME}" != "${CURRENT_SERVICE_NAME}" ]]; then
	FAILURE=1
	echo "${1}: expected service name \"${EXPECTED_SERVICE_NAME}\", found \"${CURRENT_SERVICE_NAME}\""
fi

CURRENT_COMMAND_NAME=$(jq -r ".command.commands.\"${1}\".name" "${2}")
EXPECTED_COMMAND_NAME="${CURRENT_COMMAND_NAME//_/-}"

if [[ "${EXPECTED_COMMAND_NAME}" != "${CURRENT_COMMAND_NAME}" ]]; then
	FAILURE=1
	echo "${1}: expected command name \"${EXPECTED_COMMAND_NAME}\", found \"${CURRENT_COMMAND_NAME}\""
fi

if [ "${FAILURE}" -eq 1 ]; then
	exit 1
fi
