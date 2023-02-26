#!/usr/bin/env bash
set -eu
shopt -s nullglob

pants tailor --check update-build-files --check --no-update-build-files-fmt ::

if [ -n "${CI_MERGE_REQUEST_DIFF_BASE_SHA+x}" ]; then
	pants --changed-since="${CI_MERGE_REQUEST_DIFF_BASE_SHA}" lint
	pants --changed-since="${CI_MERGE_REQUEST_DIFF_BASE_SHA}" --changed-dependees=transitive check test --pytest-args="--disable-socket --allow-unix-socket"
elif [ -n "${CI_COMMIT_BEFORE_SHA+x}" ] && [ "${CI_COMMIT_BEFORE_SHA}" != "0000000000000000000000000000000000000000" ]; then
	pants --changed-since="${CI_COMMIT_BEFORE_SHA}" lint
	pants --changed-since="${CI_COMMIT_BEFORE_SHA}" --changed-dependees=transitive check test --pytest-args="--disable-socket --allow-unix-socket"
else
	pants lint check test :: --pytest-args="--disable-socket --allow-unix-socket"
fi
