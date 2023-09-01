#!/usr/bin/env bash
set -eu

SERVICE_NAME="${1}"
SERVICE_VERSION="${2}"
ENVIRONMENT_NAME="${3}"
shift 3

for TEMPLATE_FILE in "$@"; do

	unset ADDITIONAL_ARGS
	[[ -f ${TEMPLATE_FILE%.*}.vars ]] && ADDITIONAL_ARGS="-var-file=${TEMPLATE_FILE%.*}.vars"

	echo "Deploying '${TEMPLATE_FILE%.*}' of '${SERVICE_NAME}' to '${NOMAD_ADDR}'..."

	PLAN_OUTPUT=$(nomad plan "${ADDITIONAL_ARGS}" "${TEMPLATE_FILE}" &>/dev/stdout) || {
		[[ $? -eq 255 ]] && {
			echo "${PLAN_OUTPUT}"
			exit 1
		}
	}

	CHECK_INDEX=$(awk '/Job Modify Index:/ {print $NF}' <<<"${PLAN_OUTPUT}")
	echo "Check Index: ${CHECK_INDEX}"

	RUN_OUTPUT=$(nomad run "${ADDITIONAL_ARGS}" -check-index="${CHECK_INDEX}" -detach "${TEMPLATE_FILE}" &>/dev/stdout) || {
		echo "${RUN_OUTPUT}"
		exit 1
	}

	EVALUATION_ID=$(awk '/Evaluation ID:/ {print $NF}' <<<"${RUN_OUTPUT}")
	echo "Evaluation ID: ${EVALUATION_ID}"

	if [[ -z "${EVALUATION_ID}" ]]; then
		echo "WARN: No Evaluation ID found, skipping."
		continue
	fi

	if nomad eval status -monitor "${EVALUATION_ID}" >/dev/null 2>&1; then
		continue
	fi

	DEPLOYMENT_ID=$(nomad eval status -json "${EVALUATION_ID}" | jq -e -r ".DeploymentID")

	[[ -z "${DEPLOYMENT_ID}" ]] && {
		echo "WARN: No Deployment ID found, skipping."
		continue
	}

	echo "Deployment ID: ${DEPLOYMENT_ID}"
	nomad deployment status "${DEPLOYMENT_ID}"

	mapfile -t ALLOC_IDS < <(nomad deployment status -json "${DEPLOYMENT_ID}" | jq -e -r '.TaskGroups[] | select(.PlacedCanaries != null).PlacedCanaries[]')

	if [[ ${#ALLOC_IDS[@]} -eq 0 ]]; then
		echo "WARN: No Allocation IDs found, skipping."
		continue
	fi

	echo "Allocation IDs:"
	printf "%s\n" "${ALLOC_IDS[@]}"

	for ALLOC_ID in "${ALLOC_IDS[@]}"; do
		echo "-- Allocation ${ALLOC_ID} --"
		mapfile -t JOBS < <(nomad alloc status -json "${ALLOC_ID}" | jq -e -r ".TaskStates | keys[]")
		for JOB in "${JOBS[@]}"; do
			echo "events for '${JOB}':"
			nomad alloc status -json "${ALLOC_ID}" | jq -e -r ".TaskStates.${JOB}.Events[].DisplayMessage"
			echo "stdout for '${JOB}':"
			nomad alloc logs -tail "${ALLOC_ID}" "${JOB}"
			echo "stderr for '${JOB}':"
			nomad alloc logs -stderr -tail "${ALLOC_ID}" "${JOB}"
		done
	done

	exit 1
done

if sentry-cli projects list | awk 'NR>4 {print last} {last=$4}' | grep -q "^${SERVICE_NAME}$"; then
	sentry-cli releases deploys "${SERVICE_NAME}@${SERVICE_VERSION}" new -e "${ENVIRONMENT_NAME}"
fi
