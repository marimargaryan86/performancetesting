#!/usr/bin/env bash
set -eu
shopt -s nullglob

DEPLOYMENT_ENVIRONMENT=$(basename "$1")
DEPLOYMENT_TIER=${DEPLOYMENT_ENVIRONMENT}

if [[ $DEPLOYMENT_TIER == "sandbox" ]]; then
	DEPLOYMENT_TIER="staging"
fi

DESIRED_SERVICES=()

if [ -n "${2:+x}" ]; then
	IFS="," read -r -a DESIRED_SERVICES <<<"$2"
fi

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
    - ./deploy.sh "\${service}" "\${version}" "${DEPLOYMENT_ENVIRONMENT}" \${templates}
  retry: 2
  environment:
    action: start
  variables:
    NOMAD_NAMESPACE: "${DEPLOYMENT_ENVIRONMENT}"
    NOMAD_ADDR: "\${NOMAD_${DEPLOYMENT_ENVIRONMENT^^}_ADDR}"
    NOMAD_VAR_datacenter: "\${NOMAD_${DEPLOYMENT_ENVIRONMENT^^}_DATACENTER}"
    NOMAD_VAR_environment: "${DEPLOYMENT_ENVIRONMENT}"
    NOMAD_VAR_registry_address: "\${CI_REGISTRY}"
    NOMAD_VAR_registry_password: "\${NOMAD_REGISTRY_PASSWORD}"
    NOMAD_VAR_registry_username: "\${NOMAD_REGISTRY_USERNAME}"
  needs: []
  tags:
    - docker
EOF
# editorconfig-checker-enable

services=()

for DIR in templates/*; do
	if ! [ -d "${DIR}" ]; then
		continue
	fi

	image_file="${DIR}/image.txt"
	skip_deploy="${DIR}/.skip_deploy"

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
	elif [ ${#DESIRED_SERVICES[@]} -ne 0 ]; then
		# shellcheck disable=SC2076
		if [[ ! " ${DESIRED_SERVICES[*]} " =~ " ${service_name} " ]]; then
			echo >&2 "skip: not included in services list"
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

	if [ -f "${skip_deploy}" ]; then
		# editorconfig-checker-disable
		cat <<EOF

${service_name}:
  stage: deploy
  script:
    - echo "Skipped due to ${skip_deploy}."
  needs: []
  tags:
    - shell
EOF
		# editorconfig-checker-enable
	else
		# editorconfig-checker-disable
		cat <<EOF

${service_name}:
  extends: .deploy
  environment:
    name: "${DEPLOYMENT_ENVIRONMENT}/${service_name}"
    deployment_tier: ${DEPLOYMENT_TIER}
  variables:
    NOMAD_VAR_docker_image: ${docker_image}
    service: ${service_name}
    templates: ${templates[@]}
    version: ${service_version}
EOF
		# editorconfig-checker-enable
	fi
done

if [ ${#services[@]} -eq 0 ]; then
	exit 0
fi

# editorconfig-checker-disable
cat <<EOF

verify:
  stage: verify
  image:
    name: git.snowfall.se:4567/junction/junction/service/deploy:latest
    entrypoint: [""]
  interruptible: false
  script:
    - /usr/local/bin/python3.11 -Wdefault /bin/main verify
  tags:
    - docker
  needs:
EOF
# editorconfig-checker-enable

for service in "${services[@]}"; do
	echo "    - ${service}"
done

if [ "${DEPLOYMENT_ENVIRONMENT}" == "development" ]; then
	# editorconfig-checker-disable
	cat <<EOF

.promote:
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
  tags:
    - shell
  needs:
    - verify

promote-to-production:
  extends: .promote
  script:
    - ./promote-environment.sh production ${services[@]}

promote-to-sandbox:
  extends: .promote
  script:
    - ./promote-environment.sh sandbox ${services[@]}

EOF
# editorconfig-checker-enable
fi
