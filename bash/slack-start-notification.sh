#!/usr/bin/env bash
set -eu
shopt -s nullglob

# Sending slack notification
THREAD_NUMBER=$(curl -s -X POST -H 'Content-type: application/json; charset=utf-8' \
	-H "Authorization: Bearer ${1}" \
	-d "{\"username\": \"CI Notification Bot for Allure Report\", \"channel\": \"${2}\", \"text\": \"Test job started: $CI_JOB_URL for project: *$ALLURE_PROJECT_ID*\"}" \
	https://slack.com/api/chat.postMessage | jq -r .ts)

echo "$THREAD_NUMBER"
