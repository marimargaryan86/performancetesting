#!/usr/bin/env bash
set -eu
shopt -s nullglob

THREAD_TS=${1}
JOB_LINK=${2}
# Sending slack notification
curl -s -o /dev/null \
	-X POST -H 'Content-type: application/json; charset=utf-8' \
	-H "Authorization: Bearer ${SLACK_NOTIFICATION_TOKEN}" \
	-d "{\"thread_ts\": \"${THREAD_TS}\", \"username\": \"CI Notification Bot for Allure Report\", \"channel\": \"${SLACK_NOTIFICATION_CHANNEL}\", \"text\": \"Login to allure (channel description) to analyze results: ${JOB_LINK}\"}" \
	https://slack.com/api/chat.postMessage

printf "\n"
echo "-------------------------------------------------------------------------"
echo "Pipeline job url: $CI_JOB_URL"
echo "-------------------------------------------------------------------------"
echo "Report URL: $JOB_LINK"
echo "-------------------------------------------------------------------------"
echo "Report URL is available after login with user/password to:"
echo "https://allureui.junction.dev/allure-docker-service-ui/"
echo "-------------------------------------------------------------------------"
