#!/usr/bin/env bash
set -eu

COLOR_RED="\x1b[31m"
COLOR_GREEN="\x1b[32m"
COLOR_RESET="\x1b[0m"
ROOT_DIR="$(CDPATH='' cd -- "$(dirname -- "$0")/.." && pwd)"

requirements_file="${ROOT_DIR}/vendor/requirements.txt"
has_changes=0
requirements_tmp=$(mktemp /tmp/requirements.XXXXXX)

cp "${requirements_file}" "${requirements_tmp}"

while IFS="" read -r line || [ -n "${line}" ]; do
	if echo "${line}" | grep -q "  # freeze"; then
		continue
	fi

	package="${line%==*}"
	current_version="${line##*==}"
	package_name="${package%[*}"
	pypi_info=$(curl --silent -L "https://pypi.org/pypi/${package_name}/json")
	latest_version=$(echo "${pypi_info}" | jq -r ".info.version")
	has_new_update=$(perl -e "if (version->parse(\"${latest_version}\") > version->parse(\"${current_version}\")) { print 1 } else { print 0 }" || echo "0")

	if [ "${has_new_update}" -eq "1" ]; then
		is_likely_compatible=$(perl -e "if (version->parse(\"${latest_version}\") < version->parse(\"$(("${current_version%%.*}" + 1)).0.0\")) { print 1 } else { print 0 }")

		if [ "${is_likely_compatible}" -eq "1" ]; then
			echo -e "${COLOR_GREEN}${package}==${current_version} -> ${package}==${latest_version}${COLOR_RESET}"
			sed "s/^${package/[/\\[}==${current_version}$/${package/[/\\[}==${latest_version}/g" "${requirements_file}" | sponge "${requirements_file}"
			has_changes=1
		else
			echo -e "${COLOR_RED}${package}==${current_version} -> ${package}==${latest_version}${COLOR_RESET}"
		fi
	fi
done <"${requirements_tmp}"

if [ "${has_changes}" -eq "1" ]; then
	(
		cd "${ROOT_DIR}"
		pants generate-lockfiles --resolve=python-default
	)
fi

rm "${requirements_tmp}"
