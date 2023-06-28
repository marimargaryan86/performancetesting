#!/usr/bin/env bash

set -eu
set -o pipefail
shopt -s globstar
shopt -s nullglob

pants run python/snowfall/script/validate_nomad_build_files.py -- "nomad/"

FAILURE=0
ENVIRONMENTS=("development" "production" "sandbox")

declare -A SENTRY_PROJECTS
while read -r project id; do
	SENTRY_PROJECTS["$project"]="$id"
done <<<"$(sentry-cli projects list | awk 'NR>4 {print last} {last=$4" "$2}')"

mapfile -t NOMAD_FILES < <(pants --filter-address-regex='_nomad$' peek :: | jq -r ".[] | .sources[0]")
mapfile -t DOCKER_IMAGES < <(pants --filter-target-type='docker_image' peek :: | jq -r ".[] | .address")
mapfile -t PROTOBUF_FILES < <(pants --filter-target-type="protobuf_source" list ::)

for f in "${PROTOBUF_FILES[@]}"; do
	NAMESPACE=$(dirname "${f#protobuf/}")

	if ! grep -q -e "^option go_package = \"git.snowfall.se/junction/junction/golang/protobuf/${NAMESPACE}\";$" "${f}"; then
		echo "${f}: invalid value for option \"go_package\", expected \"git.snowfall.se/junction/junction/golang/protobuf/${NAMESPACE}\""
		FAILURE=1
	fi

	if ! grep -q -e "^package ${NAMESPACE//\//.};$" "${f}"; then
		echo "${f}: invalid value for \"package\" package, expected \"${NAMESPACE//\//.}\""
		FAILURE=1
	fi
done

for i in "${DOCKER_IMAGES[@]}"; do
	SERVICE_NAME=$(basename "${i%:*}")
	SERVICE_NAME="${SERVICE_NAME//_/-}"

	if [[ "${SENTRY_PROJECTS[${SERVICE_NAME}]-0}" -eq 0 ]]; then
		echo "${SERVICE_NAME}: project does not exist in Sentry"
		FAILURE=1
	fi
done

for f in "${NOMAD_FILES[@]}"; do

	if [[ "${SENTRY_PROJECTS[$(basename "${f%/*}")]-0}" -ne 0 ]]; then

		if grep -q "SENTRY_DSN" "${f}" && ! grep -q "SENTRY_DSN.*\/${SENTRY_PROJECTS[$(basename "${f%/*}")]}\"" "${f}"; then
			echo "${f}: invalid Sentry DSN"
			FAILURE=1
		fi

	elif grep -q "SENTRY_DSN" "${f}"; then
		echo "${f}: project does not exist in Sentry"
		FAILURE=1
	fi

	CONFIG="${f%.*}.json"

	for e in "${ENVIRONMENTS[@]}"; do
		if [[ -f "${CONFIG}" ]]; then

			if [[ $(jq ".${e} | if has(\"deploy\") then .deploy else true end" "${CONFIG}") == "false" ]]; then
				continue
			fi

			VARIABLES=$(jq -e "select(.${e}.variables != null).${e}.variables" "${CONFIG}") || FAILURE=1
		fi

		if [[ -n ${VARIABLES} ]]; then
			(nomad validate -var-file /dev/stdin "${f}") <<<"${VARIABLES}" || FAILURE=1
		else
			nomad validate "${f}" || FAILURE=1
		fi

		nomad fmt -check -write=false "${f}" >/dev/null 2>&1 || {
			echo "${f}: file is not formatted correctly"
			FAILURE=1
		}

	done
done

if [[ "${FAILURE}" -eq 1 ]]; then
	exit 1
fi

if [[ -n ${NOMAD_FILES[*]} ]]; then
	pants run python/snowfall/script/validate_nomad_files.py -- "${NOMAD_FILES[@]}"
	pants run python/snowfall/script/validate_consul_templates.py -- "${NOMAD_FILES[@]}"
fi
