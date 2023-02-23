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

for i in "repo/${1}/"**/*.{nomad,vars}; do
	rm "${i}"
done

for i in nomad/**/*.nomad; do
	filename=$(basename "${i}")
	config="$(dirname "${i}")/${filename%.*}.json"
	service_name=$(basename "$(dirname "${i}")" | sed s/_/-/g)
	repo_path="repo/${1}/${service_name}"
	mkdir -p "${repo_path}"
	cp "${i}" "${repo_path}/${filename}"

	if [ -f "${config}" ]; then
		jq -r ".${1}.variables|to_entries|map(\"\\(.key)=\\(.value|tostring)\")|.[]" "${config}" >"${repo_path}/${filename%.*}.vars"
	fi
done

cp ".gitlab/deploy.gitlab-ci.yml" "repo/.gitlab-ci.yml"
cp "bash/deploy.sh" "repo/${1}/deploy.sh"
cp "bash/generate-deploy-pipeline.sh" "repo/${1}/generate-deploy-pipeline.sh"
chmod +x "repo/${1}/deploy.sh"
chmod +x "repo/${1}/generate-deploy-pipeline.sh"
cd repo
git add --all .

if [ -n "$(git status --porcelain)" ]; then
	git commit -m "${CI_COMMIT_TITLE}" -m "Refs: ${CI_PROJECT_PATH}@${CI_COMMIT_SHORT_SHA}"
	git push
fi
