#!/usr/bin/env bash

set -eu

FAILURE=0

if [ ! -f "${2}" ]; then
	echo "${2}: does not exist"
	exit 1
fi

if [ ! -f "${3}" ]; then
	echo "${3}: does not exist"
	exit 1
fi

EXPECTED_SERVICE_NAME=$(basename "$(dirname "${2}")")
CURRENT_SERVICE_NAME=$(jq -r ".command.name" "${3}")

if [[ "${EXPECTED_SERVICE_NAME}" != "${CURRENT_SERVICE_NAME}" ]]; then
	FAILURE=1
	echo "${4}: expected service name \"${EXPECTED_SERVICE_NAME}\", found \"${CURRENT_SERVICE_NAME}\""
fi

CURRENT_COMMAND_NAME=$(jq -r ".command.commands.\"${1}\".name" "${3}")
EXPECTED_COMMAND_NAME="${CURRENT_COMMAND_NAME//_/-}"

if [[ "${EXPECTED_COMMAND_NAME}" != "${CURRENT_COMMAND_NAME}" ]]; then
	FAILURE=1
	echo "${4}: expected command name \"${EXPECTED_COMMAND_NAME}\", found \"${CURRENT_COMMAND_NAME}\""
fi

mapfile -t CONFIGURED_VARS < <(perl -nle 'print $& while m{\K[A-Z0-9_]+(?=[ ]*=)}g' "${2}")
mapfile -t ALL_GLOBAL_VARS < <(jq -r ".command.params[] | .envvar" "${3}")
mapfile -t REQUIRED_GLOBAL_VARS < <(jq -r ".command.params[] | select( .required == true ) | .envvar" "${3}")
mapfile -t ALL_COMMAND_VARS < <(jq -r ".command.commands.\"${1}\".params[] | .envvar" "${3}")
mapfile -t REQUIRED_COMMAND_VARS < <(jq -r ".command.commands.\"${1}\".params[] | select( .required == true ) | .envvar" "${3}")

for v in "${CONFIGURED_VARS[@]}"; do
	if [[ ! " ${ALL_GLOBAL_VARS[*]} " == *" ${v} "* ]] && [[ ! " ${ALL_COMMAND_VARS[*]} " == *" ${v} "* ]]; then
		FAILURE=1
		echo "${2}: contains unknown configuration value \"${v}\""
	fi
done

for v in "${REQUIRED_GLOBAL_VARS[@]}"; do
	if [[ ! " ${CONFIGURED_VARS[*]} " == *" ${v} "* ]]; then
		FAILURE=1
		echo "${2}: missing required configuration value \"${v}\""
	fi
done

for v in "${REQUIRED_COMMAND_VARS[@]}"; do
	if [[ ! " ${CONFIGURED_VARS[*]} " == *" ${v} "* ]]; then
		FAILURE=1
		echo "${2}: missing required configuration value \"${v}\""
	fi
done

if [ "${FAILURE}" -eq 1 ]; then
	exit 1
fi
