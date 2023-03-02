#!/usr/bin/env bash
set -eu
shopt -s nullglob

# editorconfig-checker-disable
cat <<EOF
stages:
  - deploy
  - verify
  - promote

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
    - ./\${CI_ENVIRONMENT_TIER}/deploy.sh "\${service}" "\${version}" "\${CI_ENVIRONMENT_TIER}" \${templates}
  environment:
    action: start
  variables:
    NOMAD_NAMESPACE: "\${CI_ENVIRONMENT_TIER}"
    NOMAD_ADDR: "${2}"
    NOMAD_VAR_datacenter: "${3}"
    NOMAD_VAR_environment: "\${CI_ENVIRONMENT_TIER}"
    NOMAD_VAR_registry_address: "\${CI_REGISTRY}"
    NOMAD_VAR_registry_password: "\${NOMAD_REGISTRY_PASSWORD}"
    NOMAD_VAR_registry_username: "\${NOMAD_REGISTRY_USERNAME}"
  needs: []
  tags:
    - docker
EOF
# editorconfig-checker-enable

services=()

for DIR in "${1}"/*; do
	if ! [ -d "${DIR}" ]; then
		continue
	fi

	service_name=$(basename "${DIR}")
	docker_image=""
	service_version="latest"
	image_file="${DIR}/image.txt"
	skip_deploy="${DIR}/.skip_deploy"
	has_changed_image=0

	if [ -f "${skip_deploy}" ]; then
		echo >&2 "skip: \"${skip_deploy}\" exists"
		continue
	fi

	if ! [ -f "${image_file}" ] && grep -q 'variable "docker_image" {' "${DIR}"/*.nomad; then
		echo >&2 "skip: \"${image_file}\" is missing"
		continue
	elif [ -f "${image_file}" ]; then
		docker_image=$(cat "${image_file}")
		service_name=$(basename "${docker_image%:*}" | sed s/_/-/g)
		service_version="${docker_image##*:}"

		has_changed_image=1

		if [ -n "${CI_COMMIT_BEFORE_SHA+x}" ] && [ "${CI_COMMIT_BEFORE_SHA}" != "0000000000000000000000000000000000000000" ]; then
			if ! git diff --name-only -r "${CI_COMMIT_BEFORE_SHA}" "${CI_COMMIT_SHA}" | grep -q "^${image_file}"; then
				has_changed_image=0
			fi
		fi
	fi

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
		echo >&2 "skip: \"${DIR}\" has no Nomad template(s)"
		continue
	fi

	echo >&2 "generate: ${service_name}@${service_version}"
	services+=("${service_name}")

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

if [ ${#services[@]} -eq 0 ]; then
	exit 0
fi

# editorconfig-checker-disable
cat <<EOF

verify:
  stage: verify
  interruptible: false
  script:
    - exit 0
  tags:
    - shell
  needs:
EOF
# editorconfig-checker-enable

for service in "${services[@]}"; do
	echo "  - ${service}"
done

if [ "$(basename "${1}")" == "development" ]; then
	# editorconfig-checker-disable
	cat <<EOF

promote-to-production:
  stage: promote
  interruptible: false
  before_script:
    - mkdir -p ~/.ssh/
    - mv "\${NOMAD_SSH_KEY}" ~/.ssh/id_ed25519
    - mv "\${NOMAD_SSH_KNOWN_HOSTS}" ~/.ssh/known_hosts
    - chmod 700 ~/.ssh/
    - chmod 600 ~/.ssh/id_ed25519
    - chmod 644 ~/.ssh/known_hosts
    - git config --global user.email "\${NOMAD_GIT_EMAIL}"
    - git config --global user.name "\${NOMAD_GIT_NAME}"
    - git checkout "\${CI_DEFAULT_BRANCH}"
  script:
    - ./promote-environment.sh development production ${services[@]}
  tags:
    - shell
  needs:
    - verify
EOF
# editorconfig-checker-enable
fi
