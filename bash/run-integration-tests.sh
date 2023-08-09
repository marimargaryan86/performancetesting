#!/usr/bin/env bash
set -eu
shopt -s nullglob

ALLURE_SERVER="https://allureapi.junction.dev/allure-docker-service"
TEST_E2E_ALLURE_DIR="/allure-integration-report/"
TESTS_DIR="${1}"
TEST_E2E_HOST=${2}
TEST_E2E_TOKEN=${3}
ALLURE_PROJECT_ID=${4}
TESTING_SUITE=${5}

LOGIN_STRING='{"username": "'"$ALLURE_USERNAME"'", "password": "'"$ALLURE_PASSWORD"'"}'
# login call
curl -s -o /dev/null -X POST "${ALLURE_SERVER}/login" \
	-H "Content-Type: application/json" \
	-d "${LOGIN_STRING}" -c cookiesFile

#check allure is not busy with processing UI queries and clean in loop in case
echo "Cleaning results"
STR=$(curl -s -X GET "${ALLURE_SERVER}/clean-results?project_id=${ALLURE_PROJECT_ID}" \
	-H "accept: */*" -b cookiesFile | jq -r .meta_data.message)
SUB="Processing files for project_id"
counter=1
amount=11
until [[ "$STR" != *"$SUB"* ]]; do
	if [ $counter -gt "$amount" ]; then
		break
	fi
	echo "Allure is busy. Waiting in a loop: $counter / $amount ..."
	sleep 30
	STR=$(curl -s -X GET "${ALLURE_SERVER}/clean-results?project_id=${ALLURE_PROJECT_ID}" \
		-H "accept: */*" -b cookiesFile | jq -r .meta_data.message)
	((counter = counter + 1))
done

echo "Executing tests"
pants test --force --output=none python/snowfall/project/junction/api_automation/"${TESTS_DIR}" \
	--pytest-args="-m ${TESTING_SUITE}" \
	-- \
	--API-TOKEN="${TEST_E2E_TOKEN}" \
	--DEPARTURE_AFTER="${TEST_E2E_DEPARTURE_AFTER}" \
	--ORIGIN="${TEST_E2E_ORIGIN}" \
	--DESTINATION="${TEST_E2E_DESTINATION}" \
	--HOST="${TEST_E2E_HOST}" \
	--alluredir="${TEST_E2E_ALLURE_DIR}"
