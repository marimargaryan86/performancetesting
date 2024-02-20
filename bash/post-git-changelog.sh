#!/usr/bin/env bash

set -eu
shopt -s globstar
shopt -s nullglob

ROOT_DIR="$(CDPATH='' cd -- "$(dirname -- "$0")/.." && pwd)"
TODAY=$(printf '%(%Y-%m-%d)T\n' -1)
YESTERDAY=$(printf '%(%Y-%m-%d)T\n' $((EPOCHSECONDS - 86400)))
SLACK_MESSAGE=$(printf "*Summary for %s*\n" "${TODAY}")
ALL_COMMITS=$(git log --before "${TODAY}T04:00:00Z" --after "${YESTERDAY}T03:59:59Z" --pretty=format:"%H" --no-patch)

if [[ "${ALL_COMMITS}" != "" ]]; then
	TO_COMMIT=$(echo "${ALL_COMMITS}" | head -n 1)
	FROM_COMMIT=$(echo "${ALL_COMMITS}" | tail -n 1)
	FROM_COMMIT=$(git log --pretty=format:"%P" -n 1 "${FROM_COMMIT}")
	CHANGELOG=$(git-cliff --config vendor/git-cliff.toml "$FROM_COMMIT..$TO_COMMIT")
	SLACK_MESSAGE=$(printf "%s\nThese changes were merged yesterday:\n%s\n" "${SLACK_MESSAGE}" "${CHANGELOG}")
fi

MERGE_REQUESTS=$(pants run "${ROOT_DIR}/python/snowfall/script/generate_merge_request_update.py" -- "${SNOWMAN_GITLAB_API_TOKEN}" "${CI_PROJECT_ID}")
SLACK_MESSAGE=$(printf "%s\nThese merge requests are currently open:\n%s" "${SLACK_MESSAGE}" "${MERGE_REQUESTS}")

curl -F "text=${SLACK_MESSAGE}" -F "channel=C05F19X9J9G" -H "Authorization: Bearer ${SNOWMAN_SLACK_CHANGELOG_TOKEN}" https://slack.com/api/chat.postMessage >/dev/null
