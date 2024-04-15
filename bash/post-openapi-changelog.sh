#!/usr/bin/env bash

set -eu
shopt -s globstar
shopt -s nullglob

if [ -z "${CI_COMMIT_BEFORE_SHA+x}" ] || [ "${CI_COMMIT_BEFORE_SHA}" == "0000000000000000000000000000000000000000" ]; then
	exit 0
fi

mkdir -p "/tmp/${CI_COMMIT_BEFORE_SHA}/openapi"
git archive "${CI_COMMIT_BEFORE_SHA}:openapi" | tar -x -C "/tmp/${CI_COMMIT_BEFORE_SHA}/openapi"

for f in openapi/**/openapi.*; do
	if [ ! -f "/tmp/${CI_COMMIT_BEFORE_SHA}/${f}" ]; then
		continue
	fi

	DIFF=$(oasdiff changelog "/tmp/${CI_COMMIT_BEFORE_SHA}/${f}" "${f}" --include-checks=request-body-enum-value-removed,response-mediatype-enum-value-removed)

	if echo "$DIFF" | grep -q "No changes" || echo "$DIFF" | grep -q "No endpoint changes"; then
		continue
	fi

	API_TITLE=$(jq -r .info.title "${f}")
	printf '%s' "${DIFF}" >changelog.md
	curl -F file=@changelog.md -F "initial_comment=Changelog for \"${API_TITLE}\" rev. ${CI_COMMIT_SHORT_SHA}:" -F channels=C05CWM9H2E6 -H "Authorization: Bearer ${SNOWMAN_SLACK_CHANGELOG_TOKEN}" https://slack.com/api/files.upload >/dev/null
done
