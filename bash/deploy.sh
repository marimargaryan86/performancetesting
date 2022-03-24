#!/usr/bin/env bash
set -eu

SERVICE_NAME="${1}"
SERVICE_VERSION="${2}"
TEMPLATE_FILE="${3}"
ENVIRONMENT_NAME="${4}"

nomad plan "${TEMPLATE_FILE}" | tee /dev/stderr | grep 'Job Modify Index:' | awk -F': ' '{ print $2 }' >check-index || if [ $? -eq 255 ]; then exit 255; else true; fi
nomad run -check-index="$(cat check-index)" -preserve-counts "${TEMPLATE_FILE}"
sentry-cli releases deploys "${SERVICE_NAME}@${SERVICE_VERSION}" new -e "${ENVIRONMENT_NAME}"
