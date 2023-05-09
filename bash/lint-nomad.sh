#!/usr/bin/env bash

set -eu
set -o pipefail
shopt -s globstar
shopt -s nullglob

pants run python/snowfall/script/validate_nomad_build_files.py -- "nomad/"

ENVIRONMENTS=("development" "production")
SENTRY_PROJECTS=$(sentry-cli projects list | awk -F '|' '{if (NR>3){print $2$3}}' | sed 's/^ *//;s/ *$//')
CHANGED_SINCE=""
NOMAD_FILES=()

if [ -n "${CI_MERGE_REQUEST_DIFF_BASE_SHA+x}" ]; then
	CHANGED_SINCE="${CI_MERGE_REQUEST_DIFF_BASE_SHA}"
elif [ -n "${CI_COMMIT_BEFORE_SHA+x}" ] && [ "${CI_COMMIT_BEFORE_SHA}" != "0000000000000000000000000000000000000000" ]; then
	CHANGED_SINCE="${CI_COMMIT_BEFORE_SHA}"
fi

if [ "${CHANGED_SINCE}" == "" ]; then
	mapfile -t NOMAD_FILES < <(pants --filter-address-regex='^nomad\/.+\.nomad' list :: | sed 's/:.*$//')
else
	mapfile -t NOMAD_FILES < <(pants --changed-since="${CHANGED_SINCE}" --changed-dependents=transitive --filter-address-regex='^nomad\/.+\.nomad' list | sed 's/:.*$//')
fi

for f in "${NOMAD_FILES[@]}"; do
	if SENTRY_MATCH=$(echo "${SENTRY_PROJECTS}" | grep "$(dirname "${f}" | xargs basename)"); then
		SENTRY_ID=$(echo "$SENTRY_MATCH" | cut -d " " -f 1)

		if grep -q "SENTRY_DSN" "${f}" && ! grep "SENTRY_DSN" "${f}" | grep -q "/${SENTRY_ID}"; then
			echo "${f}: invalid Sentry DSN"
			exit 1
		fi
	elif grep -q "SENTRY_DSN" "${f}"; then
		echo "${f}: project does not exist in Sentry"
		exit 1
	fi

	FILENAME=$(basename "${f}")
	CONFIG="$(dirname "${f}")/${FILENAME%.*}.json"

	for e in "${ENVIRONMENTS[@]}"; do
		VARIABLES=()
		SKIP_DEPLOY=$(jq ".${e} | if has(\"deploy\") then .deploy else true end" "${CONFIG}")

		if [ "${SKIP_DEPLOY}" = "false" ]; then
			continue
		fi

		if [ -f "${CONFIG}" ]; then
			mapfile -t VARIABLES < <(jq -r ".${e}.variables|to_entries|map(\"-var=\\(.key)=\\(.value|tostring)\")|.[]" "${CONFIG}")
		fi

		env nomad validate "${VARIABLES[@]}" "${f}" >/dev/null
		if ! env nomad fmt -check -write=false "${f}" >/dev/null 2>&1; then
			echo -e "\e[31mFile ${f} is not formatted correctly!\e[0m"
			exit 1
		fi
	done
done

if ! [ ${#NOMAD_FILES[@]} -eq 0 ]; then
	pants run python/snowfall/script/validate_nomad_files.py -- "${NOMAD_FILES[@]}"
fi
