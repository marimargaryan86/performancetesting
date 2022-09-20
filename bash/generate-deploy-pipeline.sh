#!/usr/bin/env bash
set -eu
shopt -s nullglob

# editorconfig-checker-disable
cat <<EOF
stages:
  - deploy

make-uninterruptible:
  stage: deploy
  interruptible: false
  script:
    - echo "This job prevents pipelines from interrupting each other."
  needs: []
  tags:
    - shell

.deploy:
  stage: deploy
  image: git.snowfall.se:4567/junction/junction/pants:main
  resource_group: deploy
  script:
    - set -eu
    - ./\${CI_ENVIRONMENT_TIER}/deploy.sh "\${service}" "\${version}" "\${CI_ENVIRONMENT_TIER}" \${templates}
  environment:
    action: start
  variables:
    NOMAD_NAMESPACE: "\${CI_ENVIRONMENT_TIER}"
    NOMAD_VAR_environment: "\${CI_ENVIRONMENT_TIER}"
    NOMAD_VAR_registry_address: "\${CI_REGISTRY}"
    NOMAD_VAR_registry_password: "\${NOMAD_REGISTRY_PASSWORD}"
    NOMAD_VAR_registry_username: "\${NOMAD_REGISTRY_USERNAME}"
  needs: []
  tags:
    - docker
EOF
# editorconfig-checker-enable

for DIR in "${1}"/*; do
	if ! [ -d "${DIR}" ]; then
		continue
	fi

	image_file="${DIR}/image.txt"

	if ! [ -f "${image_file}" ]; then
		echo >&2 "skip: \"${image_file}\" is missing"
		continue
	fi

	has_changed_image=1

	if [ -n "${CI_COMMIT_BEFORE_SHA+x}" ] && [ "${CI_COMMIT_BEFORE_SHA}" != "0000000000000000000000000000000000000000" ]; then
		if ! git diff --name-only -r "${CI_COMMIT_BEFORE_SHA}" "${CI_COMMIT_SHA}" | grep -q "^${image_file}"; then
			has_changed_image=0
		fi
	fi

	docker_image=$(cat "${image_file}")
	service_name=$(basename "${docker_image%:*}" | sed s/_/-/g)
	service_version="${docker_image##*:}"
	has_changed_templates=0
	templates=()

	for TEMPLATE in "${DIR}"/*.nomad; do
		if [ -n "${CI_COMMIT_BEFORE_SHA+x}" ] && [ "${CI_COMMIT_BEFORE_SHA}" != "0000000000000000000000000000000000000000" ]; then
			if git diff --name-only -r "${CI_COMMIT_BEFORE_SHA}" "${CI_COMMIT_SHA}" | grep -q "^${TEMPLATE}"; then
				has_changed_templates=1
			fi
		else
			has_changed_templates=1
		fi

		if [ "${has_changed_image}" -eq "1" ] || [ "${has_changed_templates}" -eq "1" ]; then
			templates+=("${TEMPLATE}")
		fi
	done

	if [ "${has_changed_image}" -eq "0" ] && [ "${has_changed_templates}" -eq "0" ]; then
		echo >&2 "skip: \"${DIR}\" has no changes"
		continue
	fi

	if [ -z "${templates+x}" ]; then
		echo >&2 "skip: \"${DIR}\" has no Nomad templates"
		continue
	fi

	echo >&2 "generate: ${service_name}@${service_version}"

	# editorconfig-checker-disable
	cat <<EOF

${service_name}:
  extends: .deploy
  environment:
    name: $(basename "${1}")/${service_name}
    deployment_tier: $(basename "${1}")
  variables:
    NOMAD_VAR_docker_image: ${docker_image}
    service: ${service_name}
    templates: ${templates[@]}
    version: ${service_version}
EOF
	# editorconfig-checker-enable
done
