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
		repo_path="repo/${1}/${service_name}"
		docker_image="${i%|*}"
		mkdir -p "${repo_path}"
		echo "${docker_image}" >"${repo_path}/image.txt"

		docker login -u "${CI_REGISTRY_USER}" -p "${CI_REGISTRY_PASSWORD}" "${CI_REGISTRY}"
		docker pull "${docker_image}"
		docker tag "${docker_image}" "${docker_image%:*}:latest"
		docker push "${docker_image%:*}:latest"

	done
fi

for i in **/*.nomad; do
	root=$(echo "${i}" | cut -d "/" -f1)

	if [ "${root}" == "repo" ]; then
		continue
	fi

	service_name=$(basename "$(dirname "$i")" | sed s/_/-/g)
	repo_path="repo/${1}/${service_name}"
	mkdir -p "${repo_path}"
	cp "${i}" "${repo_path}/template.nomad"
done

cp ".gitlab/deploy.gitlab-ci.yml" "repo/.gitlab-ci.yml"
cp "bash/deploy.sh" "repo/${1}/deploy.sh"
chmod +x "repo/${1}/deploy.sh"
cd repo
git add --all .

if [ -n "$(git status --porcelain)" ]; then
	git commit -m "Deployables from ${CI_COMMIT_SHORT_SHA}: ${CI_COMMIT_MESSAGE}"
	git push
fi
