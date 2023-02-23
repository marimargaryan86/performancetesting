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

	echo "Deploying '${TEMPLATE_FILE%.*}' of '${SERVICE_NAME}'..."

	nomad plan "${ADDITIONAL_ARGS[@]}" "${TEMPLATE_FILE}" | grep 'Job Modify Index:' | awk -F': ' '{ print $2 }' >check-index
	if [ $? -eq 255 ]; then exit 1; else true; fi

	CHECK_INDEX=$(cat check-index)
	echo "Check Index: ${CHECK_INDEX}"

	if ! nomad run "${ADDITIONAL_ARGS[@]}" -check-index="${CHECK_INDEX}" -detach "${TEMPLATE_FILE}" | grep 'Evaluation ID:' | awk -F': ' '{ print $2 }' >eval-id; then
		exit 1
	else
		true
	fi

	EVALUATION_ID=$(cat eval-id)
	echo "Evaluation ID: ${EVALUATION_ID}"

	if [ "${EVALUATION_ID}" = "" ]; then
		echo "WARN: No Evaluation ID found, skipping."
		continue
	fi

	if nomad eval status -monitor "${EVALUATION_ID}" >/dev/null 2>&1; then
		continue
	else
		true
	fi

	DEPLOYMENT_ID=$(nomad eval status -json "${EVALUATION_ID}" | jq -e -r ".DeploymentID")
	echo "Deployment ID: ${DEPLOYMENT_ID}"

	if [ "${DEPLOYMENT_ID}" = "" ]; then
		echo "WARN: No Deployment ID found, skipping."
		continue
	fi

	ALLOC_IDS=$(nomad deployment status -json "${DEPLOYMENT_ID}" | jq -e -r ".TaskGroups[].PlacedCanaries | if . == null then [] else . end | add")
	echo "Allocation IDs: ${ALLOC_IDS}"

	if [ "${ALLOC_IDS}" = "" ] || [ "${ALLOC_IDS}" = "null" ]; then
		echo "WARN: No Allocation IDs found, skipping."
		continue
	fi

	while IFS= read -r ALLOC_ID; do
		echo "-- Allocation ${ALLOC_ID} --"
		JOBS=$(nomad alloc status -json "${ALLOC_ID}" | jq -e -r ".TaskStates | keys[]")
		while IFS= read -r JOB; do
			echo "stdout of '${JOB}':"
			nomad alloc logs -tail "${ALLOC_ID}" "${JOB}"
			echo "stderr of '${JOB}':"
			nomad alloc logs -stderr -tail "${ALLOC_ID}" "${JOB}"
		done <<<"${JOBS}"
	done <<<"${ALLOC_IDS}"

	exit 1
done

if sentry-cli projects list | awk -F '|' '{print $3}' | sed 's/^ *//;s/ *$//' | grep -q "${SERVICE_NAME}"; then
	sentry-cli releases deploys "${SERVICE_NAME}@${SERVICE_VERSION}" new -e "${ENVIRONMENT_NAME}"
fi
