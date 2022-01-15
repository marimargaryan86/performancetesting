#!/usr/bin/env bash
set -eu

root_dir="$(CDPATH='' cd -- "$(dirname -- "$0")/.." && pwd)"
pants_bin="${root_dir}/pants"

export VERSION="${CI_COMMIT_SHA}"
mkdir -p "$(dirname "${PANTS_PUBLISH_OUTPUT}")"
docker login -u "${CI_REGISTRY_USER}" -p "${CI_REGISTRY_PASSWORD}" "${CI_REGISTRY}"

if [ -n "${CI_MERGE_REQUEST_DIFF_BASE_SHA+x}" ]; then
	"${pants_bin}" publish --changed-since="${CI_MERGE_REQUEST_DIFF_BASE_SHA}" --changed-dependees=transitive --docker-build-args=VERSION
elif [ -n "${CI_COMMIT_BEFORE_SHA+x}" ] && [ "${CI_COMMIT_BEFORE_SHA}" != "0000000000000000000000000000000000000000" ]; then
	"${pants_bin}" publish --changed-since="${CI_COMMIT_BEFORE_SHA}" --changed-dependees=transitive --docker-build-args=VERSION
else
	"${pants_bin}" publish :: --docker-build-args=VERSION
fi
