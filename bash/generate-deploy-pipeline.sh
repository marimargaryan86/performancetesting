#!/usr/bin/env bash
set -eu

echo "stages:"
echo "  - deploy"
echo ""
echo ".deploy"
echo "  stage: deploy"
echo "  resource_group: deploy"
echo "  image: git.snowfall.se:4567/junction/junction/pants:main"
echo "  script:"
# shellcheck disable=SC2016
echo '    -./${CI_ENVIRONMENT_TIER}/deploy.sh "${service}" "${version}" "${template_file}" "${CI_ENVIRONMENT_TIER}"'
echo "  environment:"
echo "    action: start"
echo "  variables:"
# shellcheck disable=SC2016
echo '    NOMAD_NAMESPACE: "${CI_ENVIRONMENT_TIER}"'
# shellcheck disable=SC2016
echo '    NOMAD_VAR_registry_address: "${CI_REGISTRY}"'
# shellcheck disable=SC2016
echo '    NOMAD_VAR_registry_password: "${NOMAD_REGISTRY_PASSWORD}"'
# shellcheck disable=SC2016
echo '    NOMAD_VAR_registry_username: "${NOMAD_REGISTRY_USERNAME}"'
echo "  needs: []"
echo "  tags:"
echo "    - docker"
echo ""

for DIR in "${1}"/*; do
	if ! [ -d "${DIR}" ]; then
		continue
	fi

	if [ -n "${CI_COMMIT_BEFORE_SHA+x}" ] && [ "${CI_COMMIT_BEFORE_SHA}" != "0000000000000000000000000000000000000000" ]; then
		if ! git diff --name-only -r "${CI_COMMIT_BEFORE_SHA}" "${CI_COMMIT_SHA}" | grep -q "^${DIR}/"; then
			echo >&2 "skip: \"${DIR}/\" has not changed since \"${CI_COMMIT_BEFORE_SHA}\""
			continue
		fi
	fi

	image_file="${DIR}/image.txt"
	template_file="${DIR}/template.nomad"

	if ! [ -f "${image_file}" ]; then
		echo >&2 "skip: \"${image_file}\" is missing"
		continue
	fi

	if ! [ -f "${template_file}" ]; then
		echo >&2 "skip: \"${template_file}\" is missing"
		continue
	fi

	docker_image=$(cat "${DIR}/image.txt")
	service_name=$(basename "${docker_image%:*}" | sed s/_/-/g)
	service_version="${docker_image##*:}"

	echo >&2 "generate: ${service_name}@${service_version}"

	echo "${service_name}:"
	echo "  extends: .deploy"
	echo "  environment:"
	echo "    name: ${1}/${service_name}"
	echo "    deployment_tier: ${1}"
	echo "  variables:"
	echo "    NOMAD_VAR_docker_image: ${docker_image}"
	echo "    service: ${service_name}"
	echo "    template: ${template_file}"
	echo "    version: ${service_version}"
	echo ""
done
