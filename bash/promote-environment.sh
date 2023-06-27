#!/usr/bin/env bash
set -eu

TO_ENV="${1}"
SERVICES=("$@")
ARGS=()

for ((idx = 1; idx < ${#SERVICES[@]}; ++idx)); do
	ARGS+=("--include=${SERVICES[idx]}/")
done

rm -rf repo
git clone git@git.snowfall.se:junction/nomad.git repo
cd repo
git switch "${TO_ENV}" 2>/dev/null || git switch -c "${TO_ENV}"
cd ..

rsync -arv --include="*.sh" --exclude="*" "." "repo/"
rsync -arv "${ARGS[@]}" --include="*.nomad" --delete --include="image.txt" --exclude="*" "templates/" "repo/"

cd repo
git add --all .

if [ -n "$(git status --porcelain)" ]; then
	git commit --author "${CI_COMMIT_AUTHOR}" -m "${CI_COMMIT_TITLE}" -m "${CI_COMMIT_DESCRIPTION}"
	git push
fi
