#!/usr/bin/env bash
set -eu
shopt -s nullglob

ALLURE_PROJECT_ID=${1}
ALLURE_SERVER="https://allureapi.junction.dev/allure-docker-service"
allure_dir="/allure-integration-report/"

LOGIN_STRING='{"username": "'"$ALLURE_USERNAME"'", "password": "'"$ALLURE_PASSWORD"'"}'
# login
curl -s -o /dev/null -X POST "${ALLURE_SERVER}/login" \
	-H "Content-Type: application/json" \
	-d "${LOGIN_STRING}" -c cookiesFile

# grab the token
CRSF_ACCESS_TOKEN_VALUE=$(grep <cookiesFile -o 'csrf_access_token.*' | cut -f2)

counter=1
amount=$(find ${allure_dir}* -prune -print | wc -l)
for file in "${allure_dir}"*; do
	etext=$(base64 -w 0 "${file}")
	all_data+="{\"file_name\": \"${file##*/}\", \"content_base64\": \"$etext\"}"
	# Add a comma unless it is the last element in the array
	if [ $counter -lt "$amount" ]; then
		all_data+=","
	else
		all_data+=""
	fi
	((counter = counter + 1))
done
curl_all_data="{\"results\": [$all_data]}"
echo "$curl_all_data" >curl_all_data.txt

echo "Sending the results"
curl -s -o /dev/null \
	-X POST "${ALLURE_SERVER}/send-results?project_id=${ALLURE_PROJECT_ID}&force_project_creation=true" \
	-H "accept: */*" -H "Content-Type: application/json" \
	-H "X-CSRF-TOKEN: $CRSF_ACCESS_TOKEN_VALUE" \
	-d @curl_all_data.txt \
	-b cookiesFile

#check allure is not busy with processing UI queries and generating report in loop in case
echo "Generating report"
echo "Pipeline job url: $CI_JOB_URL"
GENERATE_REPORT=$(curl -s -X GET "${ALLURE_SERVER}/generate-report?project_id=${ALLURE_PROJECT_ID}&execution_name=gitlab&execution_from=${CI_JOB_URL}&execution_type=gitlab" \
	-H "accept: */*" -b cookiesFile)
STR=$(echo "${GENERATE_REPORT}" | jq -r .meta_data.message)
JOB_LINK=$(echo "${GENERATE_REPORT}" | jq -r .data.report_url)
SUB="Processing files for project_id"
counter=1
amount=11
until [[ "$STR" != *"$SUB"* ]]; do
	if [ $counter -gt "$amount" ]; then
		break
	fi
	echo "Allure is busy. Waiting in a loop: $counter / $amount ..."
	sleep 30
	GENERATE_REPORT=$(curl -s -X GET "${ALLURE_SERVER}/generate-report?project_id=${ALLURE_PROJECT_ID}&execution_name=gitlab&execution_from=${CI_JOB_URL}&execution_type=gitlab" \
		-H "accept: */*" -b cookiesFile)
	STR=$(echo "${GENERATE_REPORT}" | jq -r .meta_data.message)
	JOB_LINK=$(echo "${GENERATE_REPORT}" | jq -r .data.report_url)
	((counter = counter + 1))
done

echo "-------------------------------------------------------------------------"
echo "Report URL: $JOB_LINK"
echo "Report URL is available after login with user/password to:"
echo "https://allureui.junction.dev/allure-docker-service-ui/"
echo "-------------------------------------------------------------------------"

# Sending slack notification
curl -X POST -H 'Content-type: application/json; charset=utf-8' \
	-H "Authorization: Bearer ${SLACK_NOTIFICATION_TOKEN}" \
	-d "{\"username\": \"CI Notification Bot for Allure Report\", \"channel\": \"${SLACK_NOTIFICATION_CHANNEL}\", \"text\": \"Login to allure (channel description) to analyze results: $JOB_LINK\"}" \
	https://slack.com/api/chat.postMessage
