#!/usr/bin/env bash
set -eu
shopt -s nullglob

root_dir="$(CDPATH='' cd -- "$(dirname -- "$0")/.." && pwd)"
pants_bin="${root_dir}/pants"

if [ -n "${CI_MERGE_REQUEST_DIFF_BASE_SHA+x}" ]; then
	"${pants_bin}" package --changed-since="${CI_MERGE_REQUEST_DIFF_BASE_SHA}" --changed-dependees=transitive
elif [ -n "${CI_COMMIT_BEFORE_SHA+x}" ] && [ "${CI_COMMIT_BEFORE_SHA}" != "0000000000000000000000000000000000000000" ]; then
	"${pants_bin}" package --changed-since="${CI_COMMIT_BEFORE_SHA}" --changed-dependees=transitive
else
	"${pants_bin}" package ::
fi
