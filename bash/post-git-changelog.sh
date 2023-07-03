#!/usr/bin/env bash

set -eu
shopt -s globstar
shopt -s nullglob

TODAY=$(printf '%(%Y-%m-%d)T\n' -1)
YESTERDAY=$(printf '%(%Y-%m-%d)T\n' $((EPOCHSECONDS - 86400)))
ALL_COMMITS=$(git log --before "${TODAY}T04:00:00Z" --after "${YESTERDAY}T03:59:59Z" --pretty=format:"%h" --no-patch)

if [[ "${ALL_COMMITS}" == "" ]]; then
	exit 0
fi

TO_COMMIT=$(echo "${ALL_COMMITS}" | head -n 1)
FROM_COMMIT=$(echo "${ALL_COMMITS}" | tail -n 1)
FROM_COMMIT=$(git log --pretty=format:"%P" -n 1 "${FROM_COMMIT}")
CHANGELOG=$(git-cliff --config vendor/git-cliff.toml "$FROM_COMMIT..$TO_COMMIT")
CHANGELOG=$(printf "*Summary for %s*\n%s" "${YESTERDAY}" "${CHANGELOG}")

curl -F "text=${CHANGELOG}" -F "channel=C05F19X9J9G" -H "Authorization: Bearer ${SNOWMAN_SLACK_CHANGELOG_TOKEN}" https://slack.com/api/chat.postMessage >/dev/null
