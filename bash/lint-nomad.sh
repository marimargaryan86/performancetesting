#!/usr/bin/env bash

set -eu
set -o pipefail
shopt -s globstar
shopt -s nullglob

pants run python/snowfall/script/validate_nomad_build_files.py -- "nomad/"

FAILURE=0
ENVIRONMENTS=("development" "production" "sandbox")
CHANGED_SINCE=""
ENFORCE_FULL_LINTING=0
FULL_LINTING_REQUIRED=(
	".gitlab/pants.Dockerfile"
	"bash/lint-nomad.sh"
	"pants.ci.toml"
	"pants.toml"
	"python/snowfall/script/validate_nomad_files.py"
)

declare -A SENTRY_PROJECTS
while read -r project id; do
	SENTRY_PROJECTS["$project"]="$id"
done <<<"$(sentry-cli projects list | awk 'NR>4 {print last} {last=$4" "$2}')"

if [[ -n "${CI_MERGE_REQUEST_DIFF_BASE_SHA+x}" ]]; then
	CHANGED_SINCE="${CI_MERGE_REQUEST_DIFF_BASE_SHA}"
elif [[ -n "${CI_COMMIT_BEFORE_SHA+x}" ]] && [[ "${CI_COMMIT_BEFORE_SHA}" != "0000000000000000000000000000000000000000" ]]; then
	CHANGED_SINCE="${CI_COMMIT_BEFORE_SHA}"
fi

if [[ -n "${CI_COMMIT_SHA+x}" ]] && [[ -n "${CHANGED_SINCE}" ]]; then
	for path in "${FULL_LINTING_REQUIRED[@]}"; do
		if git diff --name-only -r "${CHANGED_SINCE}" "${CI_COMMIT_SHA}" | grep -q "^${path}"; then
			ENFORCE_FULL_LINTING=1
			break
		fi
	done
fi

if [[ "${ENFORCE_FULL_LINTING}" -eq 1 ]] || [[ -z "${CHANGED_SINCE}" ]]; then
	mapfile -t NOMAD_FILES < <(pants --filter-address-regex='_nomad$' peek :: | jq -r ".[] | .sources[0]")
else
	mapfile -t NOMAD_FILES < <(pants --changed-since="${CHANGED_SINCE}" --changed-dependents=transitive --filter-address-regex='_nomad$' peek | jq -r ".[] | .sources[0]")
fi

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
			(nomad validate -var-file /dev/stdin "${f}" >/dev/null 2>&1) <<<"${VARIABLES}" || FAILURE=1
		else
			nomad validate "${f}" >/dev/null 2>&1 || FAILURE=1
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
fi
