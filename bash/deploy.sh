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

	if ! [ -f "${image_file}" ] || ! [ -f "${template_file}" ]; then
		echo "skip: ${image_file} or ${template_file} is missing"
		continue
	fi

	NOMAD_VAR_docker_image=$(cat "${DIR}/image.txt")
	service_name=$(basename "${NOMAD_VAR_docker_image%:*}" | sed s/_/-/g)
	service_version="${NOMAD_VAR_docker_image##*:}"

	echo "deploy: ${service_name}@${service_version}"

	export NOMAD_VAR_docker_image

	nomad plan "${template_file}" | tee /dev/stderr | grep 'Job Modify Index:' | awk -F': ' '{ print $2 }' >check-index || if [ $? -eq 255 ]; then exit 255; else true; fi
	nomad run -check-index="$(cat check-index)" "${template_file}"

	sentry-cli releases deploys "${service_name}@${service_version}" new -e "${CI_ENVIRONMENT_NAME}"
done
