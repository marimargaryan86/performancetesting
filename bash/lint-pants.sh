#!/usr/bin/env bash
set -eu
shopt -s nullglob

pants tailor --check update-build-files --check ::

CHANGED_SINCE=""
ENFORCE_FULL_LINTING=0
FULL_LINTING_REQUIRED=(
	".gitlab/pants.Dockerfile"
	"bash/lint-pant.sh"
	"pants.ci.toml"
	"pants.toml"
	"vendor/"
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
	pants lint check test :: --pytest-args="--disable-socket --allow-unix-socket"
else
	pants --changed-since="${CHANGED_SINCE}" lint
	pants --changed-since="${CHANGED_SINCE}" --changed-dependents=transitive check test --pytest-args="--disable-socket --allow-unix-socket"
fi
