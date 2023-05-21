#!/usr/bin/env bash

set -eu
set -o pipefail
shopt -s globstar
shopt -s nullglob

pants run python/snowfall/script/validate_nomad_build_files.py -- "nomad/"

FAILURE=0
ENVIRONMENTS=("development" "production")
SENTRY_PROJECTS=$(sentry-cli projects list | awk -F '|' '{if (NR>3){print $2$3}}' | sed 's/^ *//;s/ *$//')
CHANGED_SINCE=""
ENFORCE_FULL_LINTING=0
FULL_LINTING_REQUIRED=(
	".gitlab/pants.Dockerfile"
	"bash/lint-nomad.sh"
	"pants.ci.toml"
	"pants.toml"
	"python/snowfall/script/validate_nomad_files.py"
)

if [ -n "${CI_MERGE_REQUEST_DIFF_BASE_SHA+x}" ]; then
	CHANGED_SINCE="${CI_MERGE_REQUEST_DIFF_BASE_SHA}"
elif [ -n "${CI_COMMIT_BEFORE_SHA+x}" ] && [ "${CI_COMMIT_BEFORE_SHA}" != "0000000000000000000000000000000000000000" ]; then
	CHANGED_SINCE="${CI_COMMIT_BEFORE_SHA}"
fi

if [ -n "${CI_COMMIT_SHA+x}" ] && [ "${CHANGED_SINCE}" != "" ]; then
	for path in "${FULL_LINTING_REQUIRED[@]}"; do
		if git diff --name-only -r "${CHANGED_SINCE}" "${CI_COMMIT_SHA}" | grep -q "^${path}"; then
			ENFORCE_FULL_LINTING=1
			break
		fi
	done
fi

if [ "${ENFORCE_FULL_LINTING}" -eq "1" ] || [ "${CHANGED_SINCE}" == "" ]; then
	mapfile -t NOMAD_FILES < <(pants --filter-address-regex='_nomad$' peek :: | jq -r ".[] | .sources[0]")
else
	mapfile -t NOMAD_FILES < <(pants --changed-since="${CHANGED_SINCE}" --changed-dependents=transitive --filter-address-regex='_nomad$' peek | jq -r ".[] | .sources[0]")
fi

for f in "${NOMAD_FILES[@]}"; do
	if SENTRY_MATCH=$(echo "${SENTRY_PROJECTS}" | grep "$(dirname "${f}" | xargs basename)"); then
		SENTRY_ID=$(echo "$SENTRY_MATCH" | cut -d " " -f 1)

		if grep -q "SENTRY_DSN" "${f}" && ! grep "SENTRY_DSN" "${f}" | grep -q "/${SENTRY_ID}"; then
			echo "${f}: invalid Sentry DSN"
			FAILURE=1
		fi
	elif grep -q "SENTRY_DSN" "${f}"; then
		echo "${f}: project does not exist in Sentry"
		FAILURE=1
	fi

	FILENAME=$(basename "${f}")
	CONFIG="$(dirname "${f}")/${FILENAME%.*}.json"

	for e in "${ENVIRONMENTS[@]}"; do
		VARIABLES=()

		if [ -f "${CONFIG}" ]; then
			SHOULD_DEPLOY=$(jq ".${e} | if has(\"deploy\") then .deploy else true end" "${CONFIG}")

			if [ "${SHOULD_DEPLOY}" = "false" ]; then
				continue
			fi

			mapfile -t VARIABLES < <(jq -r ".${e}.variables|to_entries|map(\"-var=\\(.key)=\\(.value|tostring)\")|.[]" "${CONFIG}")
		fi

		if ! env nomad validate "${VARIABLES[@]}" "${f}" >/dev/null 2>&1; then
			nomad validate "${VARIABLES[@]}" "${f}" || true
			FAILURE=1
		fi

		if ! env nomad fmt -check -write=false "${f}" >/dev/null 2>&1; then
			echo "${f}: file is not formatted correctly"
			FAILURE=1
		fi
	done
done

if [ "${FAILURE}" -eq 1 ]; then
	exit 1
fi

if ! [ ${#NOMAD_FILES[@]} -eq 0 ]; then
	pants run python/snowfall/script/validate_nomad_files.py -- "${NOMAD_FILES[@]}"
fi
