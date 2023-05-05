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

	echo "Deploying '${TEMPLATE_FILE%.*}' of '${SERVICE_NAME}' to '${NOMAD_ADDR}'..."

	if PLAN_OUTPUT=$(nomad plan "${ADDITIONAL_ARGS[@]}" "${TEMPLATE_FILE}"); then
		true # can't do ! negation above if we want to check the exact status code
	elif [ $? -eq 255 ]; then
		echo "${PLAN_OUTPUT}"
		exit 1
	fi

	CHECK_INDEX=$(echo "${PLAN_OUTPUT}" | grep "Job Modify Index:" | awk -F": " '{ print $2 }')
	echo "Check Index: ${CHECK_INDEX}"

	if ! RUN_OUTPUT=$(nomad run "${ADDITIONAL_ARGS[@]}" -check-index="${CHECK_INDEX}" -detach "${TEMPLATE_FILE}"); then
		echo "${RUN_OUTPUT}"
		exit 1
	fi

	EVALUATION_ID=$(echo "${RUN_OUTPUT}" | grep "Evaluation ID:" | awk -F": " '{ print $2 }')
	echo "Evaluation ID: ${EVALUATION_ID}"

	if [ "${EVALUATION_ID}" = "" ]; then
		echo "WARN: No Evaluation ID found, skipping."
		continue
	fi

	if nomad eval status -monitor "${EVALUATION_ID}" >/dev/null 2>&1; then
		continue
	fi

	DEPLOYMENT_ID=$(nomad eval status -json "${EVALUATION_ID}" | jq -e -r ".DeploymentID")
	echo "Deployment ID: ${DEPLOYMENT_ID}"

	if [ "${DEPLOYMENT_ID}" = "" ]; then
		echo "WARN: No Deployment ID found, skipping."
		continue
	fi

	nomad deployment status "${DEPLOYMENT_ID}"

	mapfile -t ALLOC_IDS < <(nomad deployment status -json "${DEPLOYMENT_ID}" | jq -e -r ".TaskGroups[].PlacedCanaries | if . == null then [] else . end | join(\"\\n\")")
	echo "Allocation IDs: ${ALLOC_IDS[*]}"

	if [ ${#ALLOC_IDS[@]} -eq 0 ]; then
		echo "WARN: No Allocation IDs found, skipping."
		continue
	fi

	for ALLOC_ID in "${ALLOC_IDS[@]}"; do
		echo "-- Allocation ${ALLOC_ID} --"
		mapfile -t JOBS < <(nomad alloc status -json "${ALLOC_ID}" | jq -e -r ".TaskStates | keys[]")
		for JOB in "${JOBS[@]}"; do
			echo "stdout of '${JOB}':"
			nomad alloc logs -tail "${ALLOC_ID}" "${JOB}"
			echo "stderr of '${JOB}':"
			nomad alloc logs -stderr -tail "${ALLOC_ID}" "${JOB}"
		done
	done

	exit 1
done

if sentry-cli projects list | awk -F '|' '{print $3}' | sed 's/^ *//;s/ *$//' | grep -q "${SERVICE_NAME}"; then
	sentry-cli releases deploys "${SERVICE_NAME}@${SERVICE_VERSION}" new -e "${ENVIRONMENT_NAME}"
fi
