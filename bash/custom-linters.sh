#!/usr/bin/env bash

set -eu
set -o pipefail
shopt -s globstar
shopt -s nullglob

pants run python/snowfall/script/validate_nomad_build_files.py -- "nomad/"
pants run vendor:check-jsonschema -- --schemafile nomad/config.schema.json nomad/*/**/*.json

FAILURE=0
ENVIRONMENTS=("development" "production" "sandbox")
UNSTABLE_REGEX="(v\d+(alpha|beta)\d*)|(v\d+p\d+(alpha|beta)\d*)|(v\d+test.*)"
IGNORED_UNSTABLE_RUNNABLES=(
	"python/snowfall/project/junction/extensions/service/mobile_api:main"
	"python/snowfall/project/junction/go/service/client_api:main"
	"python/snowfall/project/junction/go/service/gateway:main"
	"python/snowfall/project/junction/go/service/orders:main"
	"python/snowfall/project/junction/go/service/schedules:main"
	"python/snowfall/project/junction/go/service/trips:main"
	"python/snowfall/project/junction/service/providers/ask2go:main"
	"python/snowfall/project/junction/service/providers/benerail:main"
	"python/snowfall/project/junction/service/providers/distribusion:main"
	"python/snowfall/project/junction/service/providers/duffel:main"
	"python/snowfall/project/junction/service/providers/save_a_train:main"
	"python/snowfall/project/pay/service/companies:main"
	"python/snowfall/project/pay/service/currencies:main"
	"python/snowfall/project/pay/service/pay_api:main"
	"python/snowfall/project/pay/service/rates:main"
	"python/snowfall/project/pay/service/refunds:main"
	"python/snowfall/project/pay/service/transactions:main"
)

declare -A SENTRY_PROJECTS
while read -r project id; do
	SENTRY_PROJECTS["$project"]="$id"
done <<<"$(sentry-cli projects list | awk 'NR>4 {print last} {last=$4" "$2}')"

mapfile -t NOMAD_FILES < <(pants --filter-address-regex='_nomad$' peek :: | jq -r ".[] | .sources[0]")
mapfile -t DOCKER_REPOSITORIES < <(pants --filter-target-type='docker_image' peek :: | jq -r ".[] | select(.repository != null) | .repository")
mapfile -t PROTOBUF_FILES < <(pants --filter-target-type="protobuf_source" list ::)
mapfile -t VALID_DEBUG_INFO_ADDRESSES < <(pants --filter-address-regex='_debug_info$' peek :: | jq -r '.[] | .address')
mapfile -t UNSTABLE_PROTOS < <(pants --filter-target-type="protobuf_source" list :: | grep -P -e "${UNSTABLE_REGEX}" | xargs pants dependents --transitive)
mapfile -t CONFIG_FILES < <(pants --filter-address-regex='_config$' peek :: | jq -r '.[] | .sources[0] + "|" + .address')

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

for i in "${DOCKER_REPOSITORIES[@]}"; do
	SERVICE_NAME="${i//\//-}"

	if [[ -n ${CI_PROJECT_PATH+x} ]]; then
		SERVICE_NAME="${SERVICE_NAME#"${CI_PROJECT_PATH//\//-}-"}"
	fi

	if [[ "${SENTRY_PROJECTS[${SERVICE_NAME}]-0}" -eq 0 ]]; then
		echo "${SERVICE_NAME}: project does not exist in Sentry"
		FAILURE=1
	fi
done

POTENTIAL_DEBUG_INFO_ADDRESSES=()

for i in "${CONFIG_FILES[@]}"; do
	FILEPATH="${i%|*}"
	FILENAME=$(basename "${FILEPATH}")
	ADDRESS="${i#*|}"
	# shellcheck disable=SC2001
	DEBUG_INFO_ADDRESS=$(echo "${ADDRESS}" | sed "s/${FILENAME%.*}_config/debug_info/g")
	SHOULD_DEPLOY=$(jq ".production | if has(\"deploy\") then .deploy else true end" "${FILEPATH}")

	if [ "${SHOULD_DEPLOY}" = "false" ]; then
		continue
	fi

	POTENTIAL_DEBUG_INFO_ADDRESSES+=("${DEBUG_INFO_ADDRESS}")
done

# shellcheck disable=SC2207
POTENTIAL_DEBUG_INFO_ADDRESSES=($(for address in "${POTENTIAL_DEBUG_INFO_ADDRESSES[@]}"; do echo "${address}"; done | sort -u))
WANTED_DEBUG_INFO_ADDRESSES=()

for ADDRESS in "${POTENTIAL_DEBUG_INFO_ADDRESSES[@]}"; do
	# shellcheck disable=SC2076
	if [[ ! " ${VALID_DEBUG_INFO_ADDRESSES[*]} " =~ " ${ADDRESS} " ]]; then
		continue
	fi

	WANTED_DEBUG_INFO_ADDRESSES+=("${ADDRESS}")
done

mapfile -t RUNNABLES < <(pants peek "${WANTED_DEBUG_INFO_ADDRESSES[@]}" | jq -r '.[] | .runnable')

for RUNNABLE in "${RUNNABLES[@]}"; do
	# shellcheck disable=SC2076
	if [[ " ${IGNORED_UNSTABLE_RUNNABLES[*]} " =~ " ${RUNNABLE} " ]]; then
		continue
	fi

	# shellcheck disable=SC2076
	if [[ ! " ${UNSTABLE_PROTOS[*]} " =~ " ${RUNNABLE} " ]]; then
		continue
	fi

	echo "${RUNNABLE} depends on unstable protocol buffers:"
	pants dependencies --transitive "${RUNNABLE}" | grep -P -e "${UNSTABLE_REGEX}" | while read -r line; do echo "- $line"; done
	echo ""
	FAILURE=1
done

for f in "${NOMAD_FILES[@]}"; do
	if grep -q -e "^variable \"docker_image\" {$" "${f}"; then
		EXPECTED_REPOSITORY=$(dirname "${f#nomad/}" | sed -r 's|/|:|g; s|:([^:]*)$|/\1|; s|:|-|g')

		if [[ -n ${CI_PROJECT_PATH+x} ]]; then
			EXPECTED_REPOSITORY="${CI_PROJECT_PATH}/${EXPECTED_REPOSITORY}"
		fi

		# shellcheck disable=SC2076
		if [[ ! " ${DOCKER_REPOSITORIES[*]} " =~ " ${EXPECTED_REPOSITORY} " ]]; then
			echo "${f}: expected docker_image \"${EXPECTED_REPOSITORY}\" does not exist"
			FAILURE=1
		fi
	fi

	EXPECTED_SENTRY_PROJECT=$(dirname "${f#nomad/}" | sed -r 's|/|:|g; s|:([^:]*)$|/\1|; s|:|-|g')
	EXPECTED_SENTRY_PROJECT="${EXPECTED_SENTRY_PROJECT//\//-}"

	if [[ "${SENTRY_PROJECTS[$EXPECTED_SENTRY_PROJECT]-0}" -ne 0 ]]; then
		if grep -q "SENTRY_DSN" "${f}" && ! grep -q "SENTRY_DSN.*\/${SENTRY_PROJECTS[$EXPECTED_SENTRY_PROJECT]}\"" "${f}"; then
			echo "${f}: invalid Sentry DSN"
			FAILURE=1
		fi

	elif grep -q "SENTRY_DSN" "${f}"; then
		echo "${f}: ${EXPECTED_SENTRY_PROJECT} does not exist in Sentry"
		FAILURE=1
	fi

	CONFIG="${f%.*}.json"

	for e in "${ENVIRONMENTS[@]}"; do
		if [[ -f "${CONFIG}" ]]; then
			if [[ $(jq ".${e} | if has(\"deploy\") then .deploy else true end" "${CONFIG}") == "false" ]]; then
				continue
			fi

			traefik_entrypoints=$(jq -r ".${e}.variables.traefik_entrypoints" "${CONFIG}")

			if [[ $traefik_entrypoints != 'null' ]]; then
				if [[ "${e}" == "production" && "${traefik_entrypoints}" != "web" ]]; then
					echo "${f}: traefik_entrypoints must be 'web' for ${e}"
					FAILURE=1
				elif { [[ "${e}" == "development" || "${e}" == "sandbox" ]] && [[ "${traefik_entrypoints}" != "websecure" ]]; }; then
					echo "${f}: traefik_entrypoints must be 'websecure' for ${e}"
					FAILURE=1
				fi
			fi

			VARIABLES=$(jq -e "select(.${e}.variables != null).${e}.variables" "${CONFIG}") || FAILURE=1
		fi

		if [[ -n ${VARIABLES} ]]; then
			(nomad validate -var-file /dev/stdin "${f}" >/dev/null 2>&1) <<<"${VARIABLES}" || {
				echo "${f}: file did not validate"
				(nomad validate -var-file /dev/stdin "${f}") <<<"${VARIABLES}"
				FAILURE=1
			}
		else
			nomad validate "${f}" >/dev/null 2>&1 || {
				echo "${f}: file did not validate"
				nomad validate "${f}"
				FAILURE=1
			}
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
