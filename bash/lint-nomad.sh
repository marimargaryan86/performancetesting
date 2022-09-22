#!/usr/bin/env bash

set -eu
shopt -s globstar
shopt -s nullglob

environment=${1}
for f in nomad/**/*.nomad; do
	VARS_FILE="${f%.*}.vars.${environment}"
	ADDITIONAL_ARGS=()
	if [ -f "$VARS_FILE" ]; then
		ADDITIONAL_ARGS=("-var-file=${VARS_FILE}")
	fi
	nomad validate "${ADDITIONAL_ARGS[@]}" "${f}"
	hclfmt -require-no-change "${f}"
done
