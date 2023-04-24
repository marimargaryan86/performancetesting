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
  script:
    - ./promote-environment.sh development production ${services[@]}
  tags:
    - shell
  needs:
    - verify
EOF
# editorconfig-checker-enable
fi

services=()

for DIR in "${1}"/*; do
	if ! [ -d "${DIR}" ]; then
		continue
	fi

	image_file="${DIR}/image.txt"
	skip_deploy="${DIR}/.skip_deploy"

	if [ -f "${skip_deploy}" ]; then
		echo >&2 "skip: \"${skip_deploy}\" exists"
		continue
	fi

	if ! [ -f "${image_file}" ] && grep -q 'variable "docker_image" {' "${DIR}"/*.nomad; then
		echo >&2 "skip: \"${image_file}\" is missing"
		continue
	fi

	docker_image=""
	service_name=$(basename "${DIR}")
	service_version="latest"

	if [ -f "${image_file}" ]; then
		docker_image=$(cat "${image_file}")
		service_name=$(basename "${docker_image%:*}" | sed s/_/-/g)
		service_version="${docker_image##*:}"
	fi

	if [ -n "${CI_COMMIT_BEFORE_SHA+x}" ] && [ "${CI_COMMIT_BEFORE_SHA}" != "0000000000000000000000000000000000000000" ]; then
		if ! git diff --name-only -r "${CI_COMMIT_BEFORE_SHA}" "${CI_COMMIT_SHA}" | grep -q "^${DIR}\/"; then
			echo >&2 "skip: no changed files in \"${DIR}\""
			continue
		fi
	fi

	templates=()

	for TEMPLATE in "${DIR}"/*.nomad; do
		templates+=("${TEMPLATE}")
	done

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
  resource_group: ${service_name}
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

# editorconfig-checker-disable
cat <<EOF

verify:
  stage: verify
  interruptible: false
  script:
    - exit 0
  tags:
    - shell
EOF
# editorconfig-checker-enable

if [ ${#services[@]} -eq 0 ]; then
	exit 0
fi

# editorconfig-checker-disable
cat <<EOF
  needs:
EOF

for service in "${services[@]}"; do
	echo "  - ${service}"
done
