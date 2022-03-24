#!/usr/bin/env bash
set -eu

cat <<EOF
stages:
  - deploy
.deploy:
  stage: deploy
  image: git.snowfall.se:4567/junction/junction/pants:main
  script:
    -./\${CI_ENVIRONMENT_TIER}/deploy.sh "\${service}" "\${version}" "\${template_file}" "\${CI_ENVIRONMENT_TIER}"
  environment:
    action: start
  variables:
    NOMAD_NAMESPACE: "\${CI_ENVIRONMENT_TIER}"
    NOMAD_VAR_registry_address: "\${CI_REGISTRY}"
    NOMAD_VAR_registry_password: "\${NOMAD_REGISTRY_PASSWORD}"
    NOMAD_VAR_registry_username: "\${NOMAD_REGISTRY_USERNAME}"
  needs: []
  tags:
    - docker
EOF

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

	cat <<EOF

${service_name}:
  extends: .deploy
  environment:
    name: ${1}/${service_name}
    deployment_tier: ${1}
  variables:
    NOMAD_VAR_docker_image: ${docker_image}
    service: ${service_name}
    template: ${template_file}
    version: ${service_version}
EOF
done
