#!/usr/bin/env bash
set -eu
shopt -s nullglob

root_dir="$(CDPATH='' cd -- "$(dirname -- "$0")/.." && pwd)"
pants_bin="${root_dir}/pants"

"${pants_bin}" tailor --check update-build-files --check

if [ -n "${CI_MERGE_REQUEST_DIFF_BASE_SHA+x}" ]; then
	"${pants_bin}" lint --changed-since="${CI_MERGE_REQUEST_DIFF_BASE_SHA}"
	"${pants_bin}" check test --changed-since="${CI_MERGE_REQUEST_DIFF_BASE_SHA}" --changed-dependees=transitive
elif [ -n "${CI_COMMIT_BEFORE_SHA+x}" ] && [ "${CI_COMMIT_BEFORE_SHA}" != "0000000000000000000000000000000000000000" ]; then
	"${pants_bin}" lint --changed-since="${CI_COMMIT_BEFORE_SHA}"
	"${pants_bin}" check test --changed-since="${CI_COMMIT_BEFORE_SHA}" --changed-dependees=transitive
else
	"${pants_bin}" lint ::
	"${pants_bin}" check test ::
fi
