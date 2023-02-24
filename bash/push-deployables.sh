#!/usr/bin/env bash
set -eu
shopt -s nullglob globstar

rm -rf repo
git clone git@git.snowfall.se:junction/nomad.git repo

if [ -f "dist/deliverables.json" ]; then
	readarray -t <<<"$(jq -r '.[] | select(.publisher == "docker") | select(.published == true) | .names[0] + "|" + .target' <"dist/deliverables.json")"

	for i in "${MAPFILE[@]}"; do
		service_name=$(basename "${i#*|}" | sed s/_/-/g)
		service_name="${service_name%:*}"

		echo "--- ${service_name} ---"

		repo_path="repo/${1}/${service_name}"
		docker_image="${i%|*}"
		service_version="${docker_image##*:}"

		mkdir -p "${repo_path}"
		echo "${docker_image}" >"${repo_path}/image.txt"

		echo "docker: logging in to ${CI_REGISTRY}..."
		docker login -u "${CI_REGISTRY_USER}" -p "${CI_REGISTRY_PASSWORD}" "${CI_REGISTRY}"
		echo "docker: pulling \"${docker_image}\"..."
		docker pull "${docker_image}"
		echo "docker: tagging \"${docker_image}\" as \"${docker_image%:*}:latest\"..."
		docker tag "${docker_image}" "${docker_image%:*}:latest"
		echo "docker: pushing \"${docker_image%:*}:latest\"..."
		docker push "${docker_image%:*}:latest"

		echo "sentry: creating release \"${service_name}@${service_version}\" for \"${service_name}\"..."
		sentry-cli releases new --finalize -p "${service_name}" "${service_name}@${service_version}"
		echo "sentry: setting commits to \"Junction / Junction@${service_version}\" for \"${service_name}@${service_version}\"..."
		sentry-cli releases set-commits --commit "Junction / Junction@${service_version}" "${service_name}@${service_version}"
		echo
	done
fi

for i in repo/{development,production}/**/*.{nomad,vars}; do
	rm "${i}"
done

for i in nomad/**/*.nomad; do
	filename=$(basename "${i}")
	config="$(dirname "${i}")/${filename%.*}.json"
	service_name=$(basename "$(dirname "${i}")" | sed s/_/-/g)
	development_path="repo/development/${service_name}"
	production_path="repo/production/${service_name}"
	mkdir -p "${development_path}"
	mkdir -p "${production_path}"
	cp "${i}" "${development_path}/${filename}"

	if [ -f "${config}" ]; then
		if [ "$(jq -r ".development.deploy" "${config}")" = "false" ]; then
			touch "${development_path}/.skip_deploy"
		else
			rm -f "${development_path}/.skip_deploy"
			jq -r ".development.variables|to_entries|map(\"\\(.key)=\\(.value|tostring)\")|.[]" "${config}" >"${development_path}/${filename%.*}.vars"
		fi

		if [ "$(jq -r ".production.deploy" "${config}")" = "false" ]; then
			touch "${production_path}/.skip_deploy"
		else
			rm -f "${production_path}/.skip_deploy"
			jq -r ".production.variables|to_entries|map(\"\\(.key)=\\(.value|tostring)\")|.[]" "${config}" >"${production_path}/${filename%.*}.vars"
		fi
	fi
done

cp ".gitlab/deploy.gitlab-ci.yml" "repo/.gitlab-ci.yml"
cp "bash/deploy.sh" "repo/development/deploy.sh"
cp "bash/generate-deploy-pipeline.sh" "repo/development/generate-deploy-pipeline.sh"
chmod +x "repo/development/deploy.sh"
chmod +x "repo/development/generate-deploy-pipeline.sh"

cd repo
git add --all .

if [ -n "$(git status --porcelain)" ]; then
	git commit -m "${CI_COMMIT_TITLE}" -m "Refs: ${CI_PROJECT_PATH}@${CI_COMMIT_SHORT_SHA}"
	git push
fi
