#!/usr/bin/env bash

set -eu
shopt -s globstar
shopt -s nullglob

environment=${1}
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

	VARS_FILE="${f%.*}.vars.${environment}"
	ADDITIONAL_ARGS=()
	if [ -f "$VARS_FILE" ]; then
		ADDITIONAL_ARGS=("-var-file=${VARS_FILE}")
	fi
	nomad validate "${ADDITIONAL_ARGS[@]}" "${f}" >/dev/null
	if [[ $(nomad fmt -check -write=false "${f}") ]]; then
		exit 1
	fi
done

./pants run python/snowfall/script/validate_nomad_files.py -- nomad/**/*.nomad
