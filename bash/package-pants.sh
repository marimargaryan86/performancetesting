#!/usr/bin/env bash
set -eu
shopt -s nullglob

docker login -u "${CI_REGISTRY_USER}" -p "${CI_REGISTRY_PASSWORD}" "${CI_REGISTRY}"

root_dir="$(CDPATH='' cd -- "$(dirname -- "$0")/.." && pwd)"
pants_bin="${root_dir}/pants"

export PANTS_PUBLISH_OUTPUT="${root_dir}/dist/deliverables.json"
export VERSION="${CI_COMMIT_SHA}"

mkdir -p "$(dirname "${PANTS_PUBLISH_OUTPUT}")"

if [ -n "${CI_MERGE_REQUEST_DIFF_BASE_SHA+x}" ]; then
	"${pants_bin}" publish --changed-since="${CI_MERGE_REQUEST_DIFF_BASE_SHA}" --changed-dependees=transitive --docker-build-args=VERSION
elif [ -n "${CI_COMMIT_BEFORE_SHA+x}" ] && [ "${CI_COMMIT_BEFORE_SHA}" != "0000000000000000000000000000000000000000" ]; then
	"${pants_bin}" publish --changed-since="${CI_COMMIT_BEFORE_SHA}" --changed-dependees=transitive --docker-build-args=VERSION
else
	"${pants_bin}" publish :: --docker-build-args=VERSION
fi

if [ "${CI_COMMIT_REF_NAME}" == "${CI_DEFAULT_BRANCH}" ]; then
	readarray -t <<<"$(jq -r '.[] | select(.publisher == "docker") | select(.published == true) | .names[]' <"${PANTS_PUBLISH_OUTPUT}")"

	for i in "${MAPFILE[@]}"; do
		if [ "${CI_COMMIT_SHA}" == "$(git rev-parse --verify main)" ]; then
			docker tag "${i}" "${i%:*}:latest"
			docker push "${i%:*}:latest"
		fi
	done

	# todo: create release in Sentry
fi
