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

changed_services=()
deployed_services=()

for DIR in templates/*; do
	if ! [ -d "${DIR}" ]; then
		continue
	fi

	image_file="${DIR}/image.txt"

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

	changed_services+=("${service_name}")
	templates=()

	for TEMPLATE in "${DIR}"/*.nomad; do
		skip_file="${TEMPLATE%.*}_skip_deploy"
		if ! [ -f "${skip_file}" ]; then
			templates+=("${TEMPLATE}")
		fi
	done

	if [ -z "${templates+x}" ]; then
		echo >&2 "skip: \"${DIR}\" has no Nomad template(s) for this environment"
		continue
	fi

	echo >&2 "generate: ${service_name}@${service_version}"
	deployed_services+=("${service_name}")

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
done

if [ ${#deployed_services[@]} -ne 0 ]; then
	# editorconfig-checker-disable
	cat <<EOF

verify:
  stage: verify
  interruptible: false
  script:
    - docker login -u "\${CI_REGISTRY_USER}" -p "\${CI_REGISTRY_PASSWORD}" "\${CI_REGISTRY}"
    - docker run --rm -v "\$(pwd)/templates:/templates" --pull=always git.snowfall.se:4567/junction/junction/service/deploy:latest --env-name "${DEPLOYMENT_ENVIRONMENT}" verify --nomad-address "\${NOMAD_${DEPLOYMENT_ENVIRONMENT^^}_ADDR}" --nomad-templates-path "templates/" ${deployed_services[@]}
  tags:
    - shell
  needs:
EOF
	# editorconfig-checker-enable
	for service in "${deployed_services[@]}"; do
		echo "    - ${service}"
	done
fi

if [ "${DEPLOYMENT_ENVIRONMENT}" == "development" ] && [ ${#changed_services[@]} -ne 0 ]; then
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
EOF

	if [ ${#deployed_services[@]} -ne 0 ]; then
		# editorconfig-checker-disable
		cat <<EOF
  needs:
    - verify
EOF
		# editorconfig-checker-enable
	fi

	# editorconfig-checker-disable
	cat <<EOF

promote-to-production:
  extends: .promote
  script:
    - ./promote-environment.sh production ${changed_services[@]}

promote-to-sandbox:
  extends: .promote
  script:
    - ./promote-environment.sh sandbox ${changed_services[@]}

EOF
# editorconfig-checker-enable
fi
