#!/usr/bin/env bash
set -eu
shopt -s nullglob globstar extglob

rm -rf repo
git clone git@git.snowfall.se:junction/nomad.git repo

ENVIRONMENTS=("development" "production" "sandbox")

for e in "${ENVIRONMENTS[@]}"; do
	cd repo
	git switch "${e}" 2>/dev/null || git switch --orphan "${e}"
	cd ..

	if [[ "${e}" == "development" ]]; then
		if [[ -f "dist/deliverables.json" ]]; then
			readarray -t <<<"$(jq -r '.[] | select(.publisher == "docker") | select(.published == true) | .names[0] + "|" + .target' <"dist/deliverables.json")"

			for i in "${MAPFILE[@]}"; do
				docker_image="${i%|*}"
				service_version="${docker_image##*:}"
				service_name="${docker_image%:*}"
				service_name="${service_name#"${CI_REGISTRY}/"}"
				service_name="${service_name#"${CI_PROJECT_PATH}/"}"
				service_name="${service_name//\//-}"

				echo "--- ${service_name} ---"

				repo_path="repo/templates/${service_name}"

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

		for i in repo/templates/**/*.nomad; do
			rm "${i}"
		done
	fi

	for i in repo/templates/**/{.skip_deploy,*_skip_deploy,*.vars}; do
		rm "${i}"
	done

	for i in nomad/**/*.nomad; do
		filename=$(basename "${i}")
		config="${i%.*}.json"
		service_name=$(dirname "${i#"nomad/"}" | sed s!/!-!g)
		template_path="repo/templates/${service_name}"

		mkdir -p "${template_path}"

		if [[ "${e}" == "development" ]]; then
			cp "${i}" "${template_path}/${filename}"
		fi

		if [[ -f "${config}" ]]; then
			if [[ "$(jq -r ".${e}.deploy" "${config}")" == "false" ]]; then
				touch "${template_path}/${filename%.*}_skip_deploy"
			else
				jq -r ".${e}.variables" "${config}" >"${template_path}/${filename%.*}.vars"
			fi
		fi
	done

	# clean up our past mistakes
	find repo -type d -empty -delete
	cd repo && rm -rf !(templates) && cd ..

	cp ".gitlab/deploy.gitlab-ci.yml" "repo/.gitlab-ci.yml"
	cp "bash/deploy.sh" "repo/deploy.sh"
	cp "bash/promote-environment.sh" "repo/promote-environment.sh"
	cp "bash/generate-deploy-pipeline.sh" "repo/generate-deploy-pipeline.sh"

	chmod +x "repo/deploy.sh"
	chmod +x "repo/generate-deploy-pipeline.sh"
	chmod +x "repo/promote-environment.sh"

	cd repo
	git add --all .

	if [[ -n "$(git status --porcelain)" ]]; then
		git commit --author "${CI_COMMIT_AUTHOR}" -m "${CI_COMMIT_TITLE}" -m "Refs: ${CI_PROJECT_PATH}@${CI_COMMIT_SHORT_SHA}"
		git push -u origin "${e}"
	fi

	cd ..
done
