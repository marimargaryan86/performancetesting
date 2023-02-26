#!/usr/bin/env bash
set -eu

export VERSION="${CI_COMMIT_SHA}"
export REGISTRY="${CI_DEPENDENCY_PROXY_GROUP_IMAGE_PREFIX}/"
mkdir -p "$(dirname "${PANTS_PUBLISH_OUTPUT}")"
docker login -u "${CI_REGISTRY_USER}" -p "${CI_REGISTRY_PASSWORD}" "${CI_REGISTRY}"
docker login -u "${CI_DEPENDENCY_PROXY_USER}" -p "${CI_DEPENDENCY_PROXY_PASSWORD}" "${CI_DEPENDENCY_PROXY_SERVER}"

if [ -n "${CI_MERGE_REQUEST_DIFF_BASE_SHA+x}" ]; then
	pants publish --changed-since="${CI_MERGE_REQUEST_DIFF_BASE_SHA}" --changed-dependees=transitive --docker-build-args=REGISTRY --docker-build-args=VERSION
elif [ -n "${CI_COMMIT_BEFORE_SHA+x}" ] && [ "${CI_COMMIT_BEFORE_SHA}" != "0000000000000000000000000000000000000000" ]; then
	pants publish --changed-since="${CI_COMMIT_BEFORE_SHA}" --changed-dependees=transitive --docker-build-args=REGISTRY --docker-build-args=VERSION
else
	pants publish :: --docker-build-args=REGISTRY --docker-build-args=VERSION
fi
