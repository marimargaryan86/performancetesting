#!/usr/bin/env bash

set -eu

FAILURE=0

if [ ! -f "${3}" ]; then
	echo "${3}: does not exist"
	exit 1
fi

mapfile -t REQUIRED_VARS < <(jq -r ".command.params[] | select( .required == true ) | .envvar" "${3}")

for v in "${REQUIRED_VARS[@]}"; do
	if ! grep -q "${v}" "${2}"; then
		FAILURE=1
		echo "${2}: missing required configuration value \"${v}\""
	fi
done

mapfile -t REQUIRED_VARS < <(jq -r ".command.commands.\"${1}\".params[] | select( .required == true ) | .envvar" "${3}")

for v in "${REQUIRED_VARS[@]}"; do
	if ! grep -q "${v}" "${2}"; then
		FAILURE=1
		echo "${2}: missing required configuration value \"${v}\""
	fi
done

if [ "${FAILURE}" -eq 1 ]; then
	exit 1
fi
