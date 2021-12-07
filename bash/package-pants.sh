#!/usr/bin/env bash
set -eu
shopt -s nullglob

docker login -u "${CI_REGISTRY_USER}" -p "${CI_REGISTRY_PASSWORD}" "${CI_REGISTRY}"

root_dir="$(CDPATH='' cd -- "$(dirname -- "$0")/.." && pwd)"
pants_bin="${root_dir}/pants"
nomad_dir="${root_dir}/nomad"

export PANTS_PUBLISH_OUTPUT="${root_dir}/dist/deliverables.json"
export VERSION="${CI_COMMIT_SHA}"

mkdir -p "$(dirname "${PANTS_PUBLISH_OUTPUT}")" "${nomad_dir}"

if [ -n "${CI_MERGE_REQUEST_DIFF_BASE_SHA+x}" ]; then
	"${pants_bin}" publish --changed-since="${CI_MERGE_REQUEST_DIFF_BASE_SHA}" --changed-dependees=transitive --docker-build-args=VERSION
elif [ -n "${CI_COMMIT_BEFORE_SHA+x}" ] && [ "${CI_COMMIT_BEFORE_SHA}" != "0000000000000000000000000000000000000000" ]; then
	"${pants_bin}" publish --changed-since="${CI_COMMIT_BEFORE_SHA}" --changed-dependees=transitive --docker-build-args=VERSION
else
	"${pants_bin}" publish :: --docker-build-args=VERSION
fi

if [ "${CI_COMMIT_REF_NAME}" == "${CI_DEFAULT_BRANCH}" ] && [ -f "${PANTS_PUBLISH_OUTPUT}" ]; then
	readarray -t <<<"$(jq -r '.[] | select(.publisher == "docker") | select(.published == true) | .names[0] + "|" + .target' <"${PANTS_PUBLISH_OUTPUT}")"

	for i in "${MAPFILE[@]}"; do
		export DOCKER_IMAGE="${i%|*}"
		pants_target="${i#*|}"

		if [ "${CI_COMMIT_SHA}" == "$(git log -n 1 --pretty=format:"%H" "origin/${CI_DEFAULT_BRANCH}")" ]; then
			docker tag "${DOCKER_IMAGE}" "${DOCKER_IMAGE%:*}:latest"
			docker push "${DOCKER_IMAGE%:*}:latest"
		fi

		# todo: create release in Sentry

		service_name=$(basename "${pants_target%:*}")
		job_file="${pants_target%:*}/${service_name}.nomad"
		nomad_file="${nomad_dir}/${service_name}.nomad"

		# shellcheck disable=SC2016
		envsubst '${DOCKER_IMAGE} ${CI_REGISTRY_USER} ${CI_REGISTRY_PASSWORD} ${CI_REGISTRY}' <"${job_file}" >"${nomad_file}"
		nomad validate "${nomad_file}"
		nomad plan "${nomad_file}" | tee /dev/stderr | grep 'Job Modify Index:' | awk -F': ' '{ print $2 }' >check-index || if [ $? -eq 255 ]; then exit 255; else true; fi
		nomad run -check-index="$(cat check-index)" "${nomad_file}"
	done
fi
