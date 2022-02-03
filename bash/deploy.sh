#!/usr/bin/env bash
set -eu

for DIR in "${1}"/*; do
	if ! [ -d "${DIR}" ]; then
		continue
	fi

	if ! git diff-tree --no-commit-id --name-only -r "${CI_COMMIT_SHA}" | grep -q "${DIR}/"; then
		echo "skip: ${DIR} has not changed"
		continue
	fi

	image_file="${DIR}/image.txt"
	template_file="${DIR}/template.nomad"
	job_file="${DIR}/job.nomad"

	if ! [ -f "${image_file}" ] || ! [ -f "${template_file}" ]; then
		echo "skip: ${image_file} or ${template_file} is missing"
		continue
	fi

	DOCKER_IMAGE=$(cat "${DIR}/image.txt")
	service_name=$(basename "${DOCKER_IMAGE%:*}" | sed s/_/-/g)
	service_version="${DOCKER_IMAGE##*:}"

	echo "deploy: ${service_name}@${service_version}"

	export DOCKER_IMAGE
	# shellcheck disable=SC2016
	envsubst '${DOCKER_IMAGE} ${NOMAD_REGISTRY_USERNAME} ${NOMAD_REGISTRY_PASSWORD} ${CI_REGISTRY}' <"${template_file}" >"${job_file}"

	nomad plan "${job_file}" | tee /dev/stderr | grep 'Job Modify Index:' | awk -F': ' '{ print $2 }' >check-index || if [ $? -eq 255 ]; then exit 255; else true; fi
	nomad run -check-index="$(cat check-index)" "${job_file}"

	sentry-cli releases deploys "${service_name}@${service_version}" new -e "${CI_ENVIRONMENT_NAME}"
done
