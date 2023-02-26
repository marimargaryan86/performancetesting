#!/usr/bin/env bash

set -eu
shopt -s globstar
shopt -s nullglob

ENVIRONMENT=${1}
SENTRY_PROJECTS=$(sentry-cli projects list | awk -F '|' '{if (NR>3){print $2$3}}' | sed 's/^ *//;s/ *$//')

for f in nomad/**/*.nomad; do
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
	VARIABLES=()

	if [ -f "${CONFIG}" ]; then
		mapfile -t VARIABLES < <(jq -r ".${ENVIRONMENT}.variables|to_entries|map(\"-var=\\(.key)=\\(.value|tostring)\")|.[]" "${CONFIG}")
	fi

	nomad validate "${VARIABLES[@]}" "${f}" >/dev/null
	if [[ $(nomad fmt -check -write=false "${f}") ]]; then
		exit 1
	fi
done

pants run python/snowfall/script/validate_nomad_files.py -- nomad/**/*.nomad
