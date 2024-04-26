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

	if hcl2json "${TEMPLATE_FILE}" | jq -e 'try((.job[][].group[][].service[] | select(.port == "grpc")) != null)' >/dev/null; then
		CONSUL_SERVICE_NAME=$(
			hcl2json "${TEMPLATE_FILE}" |
				jq -er --arg ENVIRONMENT_NAME "${ENVIRONMENT_NAME}" '
				try(
				if (.job[][].group[][].service[] | select(.port == "grpc").name) == "${JOB}-${var.environment}"
				then (.job | to_entries[].key) + "-${var.environment}"
				else (.job[][].group[][].service[] | select(.tags[] == "grpc").name)
				end |
				sub("\\${var\\.environment}";$ENVIRONMENT_NAME))'
		)

		if [[ -n ${CONSUL_SERVICE_NAME} ]]; then
			echo -n "[${CONSUL_SERVICE_NAME}]: register grpc service-defaults in consul: "
			jq -nc --arg Name "${CONSUL_SERVICE_NAME}" \
				'{"Kind": "service-defaults", $Name, "LocalRequestTimeoutMs": 50000, "Protocol": "grpc"}' |
				curl -sL -X PUT "${NOMAD_ADDR%:*}:8500/v1/config" --data @-
			echo

			echo -n "[${CONSUL_SERVICE_NAME}]: setting 50s service-router timeout in consul: "
			jq -nc --arg Name "${CONSUL_SERVICE_NAME}" \
				'{"Kind":"service-router", $Name, "Routes": [{"Match": {"HTTP":{}}, "Destination": {"RequestTimeout": "50s"}}]}' |
				curl -sL -X PUT "${NOMAD_ADDR%:*}:8500/v1/config" --data @-
			echo
		else
			echo "Found grpc service in ${TEMPLATE_FILE} (${SERVICE_NAME}), but couldn't find correct service name for grpc."
		fi
	fi

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
			nomad alloc status -json "${ALLOC_ID}" | jq -e -r ".TaskStates.\"${JOB}\".Events[].DisplayMessage"
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
