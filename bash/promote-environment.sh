#!/usr/bin/env bash
set -eu

FROM_ENV="${1}"
TO_ENV="${2}"

rsync -arv --include="*/" --include="*.nomad" --include="*.sh" --include="image.txt" --exclude="*" "${FROM_ENV}/" "${TO_ENV}/"
git add --all .

if [ -n "$(git status --porcelain)" ]; then
	git commit -m "${CI_COMMIT_TITLE}" -m "Refs: ${CI_PROJECT_PATH}@${CI_COMMIT_SHORT_SHA}"
	git push
fi
