#!/usr/bin/env bash
set -eu

FROM_ENV="${1}"
TO_ENV="${2}"
SERVICES=("$@")
ARGS=()

for ((idx = 2; idx < ${#SERVICES[@]}; ++idx)); do
	ARGS+=("--include=${SERVICES[idx]}/")
done

rsync -arv --include="*.sh" --exclude="*" "${FROM_ENV}/" "${TO_ENV}/"
rsync -arv "${ARGS[@]}" --include="*.nomad" --include="image.txt" --exclude="*" "${FROM_ENV}/" "${TO_ENV}/"

git add --all .

if [ -n "$(git status --porcelain)" ]; then
	git commit -m "${CI_COMMIT_TITLE}" -m "Refs: ${CI_PROJECT_PATH}@${CI_COMMIT_SHORT_SHA}"
	git push
fi
