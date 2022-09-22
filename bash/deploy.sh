#!/usr/bin/env bash
set -eu

SERVICE_NAME="${1}"
SERVICE_VERSION="${2}"
ENVIRONMENT_NAME="${3}"
ARGS=("$@")

for ((idx = 3; idx < ${#ARGS[@]}; ++idx)); do
	TEMPLATE_FILE="${ARGS[idx]}"
	VARS_FILE="${TEMPLATE_FILE%.*}.vars"

	ADDITIONAL_ARGS=()
	if [ -f "$VARS_FILE" ]; then
		ADDITIONAL_ARGS=("-var-file=${VARS_FILE}")
	fi
	nomad plan "${ADDITIONAL_ARGS[@]}" "${TEMPLATE_FILE}" | tee /dev/stderr | grep 'Job Modify Index:' | awk -F': ' '{ print $2 }' >check-index
	if [ $? -eq 255 ]; then exit 255; else true; fi
	nomad run "${ADDITIONAL_ARGS[@]}" -check-index="$(cat check-index)" "${TEMPLATE_FILE}"
done

sentry-cli releases deploys "${SERVICE_NAME}@${SERVICE_VERSION}" new -e "${ENVIRONMENT_NAME}"
