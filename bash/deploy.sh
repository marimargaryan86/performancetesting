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

	nomad plan "${ADDITIONAL_ARGS[@]}" "${TEMPLATE_FILE}" | tee /dev/stderr | grep 'Job Modify Index:' | awk -F': ' '{ print $2 }' >check-index
	if [ $? -eq 255 ]; then exit 1; else true; fi

	if ! nomad run "${ADDITIONAL_ARGS[@]}" -check-index="$(cat check-index)" -detach "${TEMPLATE_FILE}" | tee /dev/stderr | grep 'Evaluation ID:' | awk -F': ' '{ print $2 }' >eval-id; then
		exit 1
	else
		true
	fi

	if [ "$(cat eval-id)" = "" ] || nomad eval status -monitor "$(cat eval-id)" >/dev/null 2>&1; then
		continue
	else
		true
	fi

	DEPLOYMENT_ID=$(nomad eval status -json "$(cat eval-id)" | jq -r ".DeploymentID")
	ALLOC_IDS=$(nomad deployment status -json "${DEPLOYMENT_ID}" | jq -r ".TaskGroups[].PlacedCanaries | add")

	echo "Deployment ID: ${DEPLOYMENT_ID}"

	while IFS= read -r ALLOC_ID; do
		echo "-- Allocation ${ALLOC_ID} --"
		JOBS=$(nomad alloc status -json "${ALLOC_ID}" | jq -r ".TaskStates | keys[]")
		while IFS= read -r JOB; do
			echo "stdout of '${JOB}':"
			nomad alloc logs -tail "${ALLOC_ID}" "${JOB}"
			echo "stderr of '${JOB}':"
			nomad alloc logs -stderr -tail "${ALLOC_ID}" "${JOB}"
		done <<<"${JOBS}"
	done <<<"${ALLOC_IDS}"

	exit 1
done

sentry-cli releases deploys "${SERVICE_NAME}@${SERVICE_VERSION}" new -e "${ENVIRONMENT_NAME}"
