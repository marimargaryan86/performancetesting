#!/bin/bash
# tests/schedule_tests/run_e2e_tests.sh
# shellcheck disable=SC2012,SC2059,SC2317
# using ls to find most recent file, variables in printf are fine
# "Command appears to be unreachable" - I'm sure it is reachable
# End to End script
# If run with no options, it runs function `run_all_timeslice`
# To run the pre-timeslice versions, run with option `run_all_classic`
# Run `run_e2e_tests.sh list` to see available functions
# Requires these external env vars:
# E2E_TEST_YML_FILE, the full S3 path to a test YML file

data_root="${E2E_DATA_ROOT:-$HOME/feeds}"
data_input_dir="${data_root}"/input_data/
data_transitional_dir="${data_root}"/transitional_data
known_good_dir="${data_root}"/known_good/
audit_dir="${data_root}"/logs
data_output_dir="${data_root}"/output_data
logs_dir="${data_root}"/logs
test_data_dir="${data_root}"/test_data
progress_log_file="${data_root}"/logs/progress_$(date +"%Y-%m-%dT%H:%M:%S").log
export_prog=cmd/schedules-export/schedules-export
s3_bucket=junction-schedules-export
s3_root=Test
s3_test_data=test_data
s3_test_data_path="${s3_root}/${s3_test_data}"/
s3_logs_path=s3://"${s3_bucket}/${s3_test_data_path}"logs/
mongodb="${MONGODB:-mongodb://localhost:27017}"

set -e

## FUNCTIONS

#<editor-fold desc="All Shell Functions">

progress_log() {
	# shellcheck disable=SC2124
	all_args="$@"
	echo "$(date) ${all_args}" >>"${progress_log_file}"
	echo "${all_args}"
}

run_startup() {
	printf "\n==========================  Starting run_e2e_tests.sh  ===============================\n"
	printf "\t\t\t(e2e.sh list to list available functions)\n\n"
	printf "\t\t\t(Log file is: ${progress_log_file})\n\n"

	mkdir -p "$data_input_dir"
	mkdir -p "$data_transitional_dir"
	mkdir -p "$audit_dir"
	mkdir -p "$data_output_dir"
	mkdir -p "$logs_dir"
	mkdir -p "$test_data_dir"
	progress_log "Run startup All OK"
}

run_import() {
	printf "\n============================ RUN gtfs-timeslice-import time-slice version ==================\n"
	# NB same program for time-sluice or classic; Runs 'classic' if no time-slice definition file specified.
	progress_log "Run Import (All GTFS files) from feeds/input_data to feeds/transitional_data/pX"
	# eg import from feeds/input_data/*.zip to feeds/transitional_data/ BIN files.
	mkdir -p "${data_transitional_dir}"
	rm -rf "${data_transitional_dir:?}"/*
	echo "Building gtfs-timeslice-import.go"
	cd golang || exit
	go build -o cmd/gtfs-timeslice-import/gtfs-timeslice-import cmd/gtfs-timeslice-import/*.go

	progress_log "gtfs-timeslice-import input dir: ${data_input_dir}, output_dir: ${data_transitional_dir}"

	unset run_opt
	if [ -n "$RUN_DATE" ]; then
		run_opt="--run-date=${RUN_DATE}"
	fi
	unset timeslice_opt
	if [ -n "${time_slice_json}" ]; then
		timeslice_opt="--time-slice-json=${time_slice_json}"
	else
		echo "No time_slice_json set, will run 'classic' single unified data set"
	fi

	printf "============= gtfs-timeslice-import =============\n\n"
	progress_log "gtfs-timeslice-import options: run options: ${run_opt} timeslice-file: ${timeslice_opt}"
	cmd/gtfs-timeslice-import/gtfs-timeslice-import \
		--input-dir="${data_input_dir}" \
		--output-dir="${data_transitional_dir}" "${run_opt}" "${timeslice_opt}"

	cd - || exit
	ls -l "${data_transitional_dir}"
	file_count=$(ls -1q "${data_transitional_dir}" | wc -l)
	if [ "${file_count}" -eq "0" ]; then
		progress_log "ERROR from gtfs-timeslice-import.go NO FILES in ${data_transitional_dir}"
		exit 22
	fi
	progress_log "Completed gtfs-timeslice-import.go"
	printf "\n============================ COMPLETED gtfs-timeslice-import ==================\n\n"
}

_get_s3_tar_file() {
	#	$1 is the S3 file path
	#   $2 is the file description
	#   $3 is the target directory

	if [ $# -ne 3 ]; then
		progress_log "ERROR need 3 (S3_path, name, destination_dir) parameters to _get_s3_tar_file, got $*"
		return
	fi

	tar_file_s3=$1
	target_dir=$3
	progress_log "(_get_s3_tar_file) Downloading <$2> S3 file  ${tar_file_s3} - > ${target_dir}"
	S3_EXIT_CODE=0
	aws s3 cp "${tar_file_s3}" "${target_dir}" || S3_EXIT_CODE=$?
	if [ $S3_EXIT_CODE -ne 0 ]; then
		echo aws s3 cp "${tar_file_s3}" "${target_dir}" failed \($S3_EXIT_CODE\)
		exit 13
	fi

	tar_file_name="$(basename "$tar_file_s3")"
	tar_file=$(find "${target_dir}" -maxdepth 1 -name "${tar_file_name}")
	if [ -z "${tar_file}" ]; then
		echo Missing test file "${tar_file}" in "${target_dir}"
		exit 14
	fi
	LAST_TAR_FILE="${tar_file}"
	progress_log "Downloaded $2 TAR file to: ${LAST_TAR_FILE}"
}

_extract_tar_file() {
	# $1 is the TAR file path (must be full path)
	# Extracted in the  same dir
	# If tarfilename ends '.gz', use tar -xz, else just -x
	if [ $# -ne 1 ]; then
		progress_log "ERROR needs target TAR file path in  _extract_tar_file, got $*"
		return
	fi
	if [ ! -f "$1" ]; then
		progress_log "ERROR TAR file $1 does not exist"
		return
	fi
	tar_file=$1
	echo SHA1SUM of the TAR file is:
	shasum "${tar_file}"
	echo "Expand then delete the TAR file $tar_file"
	fileExt="${tar_file##*.}"
	# no really, see https://www.gnu.org/software/bash/manual/html_node/Shell-Parameter-Expansion.html
	if [ "$fileExt" = ".gz" ]; then
		tarOpts="-xz"
	else
		tarOpts="-x"
	fi
	# IF the tar file is created by MacOS and then un-tar by Linux,
	# gets lots if warnings like
	# tar: Ignoring unknown extended header keyword 'LIBARCHIVE.xattr.com.apple.quarantine'
	# suppress these
	tar "${tarOpts}" -f "${tar_file}" -C "$(dirname "${tar_file}")" \
		2> >(grep -v "Ignoring unknown extended header keyword")
	rm -f "${tar_file}"
	rm -f "${data_input_dir}"/._*.zip #No idea WTF these are or where they came from
	echo "files extracted from TAR ${tar_file}:"
	ls -l "$(dirname "${tar_file}")"

}

# shellcheck disable=SC2120
run_fetch_test_data() {
	if [ -z "${E2E_TEST_YML_FILE}" ]; then
		echo "Missing Env Var E2E_TEST_YML_FILE, must be the S3 path to a test YML file"
		exit 10
	fi

	printf "\n============================ FETCH TEST DATA FROM S3 ==================\n\n"
	# First get the test YML file
	progress_log "Fetch test data file  ${E2E_TEST_YML_FILE} from S3: to test input in ${data_input_dir}"
	rm -rf "${data_input_dir}"
	rm -rf "${test_data_dir}"
	if ! aws s3 cp "${E2E_TEST_YML_FILE}" "${test_data_dir}/"; then
		echo aws s3 cp "${E2E_TEST_YML_FILE}" failed
		exit 11
	fi
	TEST_YML_FILE=$(find "${test_data_dir}" -maxdepth 1 -name "*.yml")
	if [ -z "${TEST_YML_FILE}" ]; then
		echo Missing test file in "${test_data_dir}"
		exit 12
	fi
	echo "Test file is: ${TEST_YML_FILE}"

	# List the test-details section of the yML file
	test_details=$(yq '."test-details"' "${TEST_YML_FILE}")
	echo Details for this test file:
	echo "${test_details}"

	# Now get the data TAR file, get the name from the test YML file
	tar_file_s3=$(yq '."test-details"."gtfs-tar-file"' "${TEST_YML_FILE}" | tr -d '"')
	_get_s3_tar_file "${tar_file_s3}" "Test Data" "${data_input_dir}"
	_extract_tar_file "${data_input_dir}/$(basename "${tar_file_s3}")"

	# Now get the time-slice.json config file specified for this test
	time_slice_s3=$(yq '."test-details"."time-slice-json"' "${TEST_YML_FILE}" | tr -d '"')
	if [ -z "$time_slice_s3" ]; then
		progress_log "test-details.time-slice-json not defined in test config file  ${TEST_YML_FILE}, exiting"
		exit 20
	fi
	_get_s3_tar_file "${time_slice_s3}" "time slice definition.json" "${test_data_dir}"
	time_slice_json="$LAST_TAR_FILE"
	progress_log "Time slice file : ${time_slice_json}"

	printf "\n============================ FETCH TEST DATA COMPLETE ==================\n\n"
}

get_known_good_filename() {
	# get KG filename from test.yml, sets into KNOWN_GOOD_TAR_FILE
	TEST_YML_FILE=$(find "${test_data_dir}" -maxdepth 1 -name "*.yml")
	if [ -z "${TEST_YML_FILE}" ]; then
		echo Missing test file in "${test_data_dir}"
		exit 22
	fi
	KNOWN_GOOD_TAR_FILE=$(yq '."test-details"."known-good-files"' "${TEST_YML_FILE}" | tr -d '"')
	# Note returns literal string "null" if no file!
	if [ -z "${KNOWN_GOOD_TAR_FILE}" ] || [ "${KNOWN_GOOD_TAR_FILE}" == "null" ]; then
		progress_log "NO known-good files for these tests"
		unset KNOWN_GOOD_TAR_FILE
	else
		progress_log "KNOWN_GOOD_TAR_FILE for these tests is ${KNOWN_GOOD_TAR_FILE} (get_known_good_filename)"
	fi
}

run_export() {
	printf "\n============================ RUN schedules-exporter ==================\n"
	printf "Run schedules-exporter.go (Create final BIN files)\n"
	printf "... from feeds/transitional_data to $data_output_dir\n"

	progress_log "Run schedules-export.go"
	rm -rf "${data_output_dir}"
	mkdir -pv "${data_output_dir}"
	cd golang || exit
	echo "Building schedules-export.go"
	go build -o "${export_prog}" cmd/schedules-export/*.go
	"${export_prog}" --input-dir="${data_transitional_dir}" --output-dir="${data_output_dir}"
	ls -l "${data_output_dir}"
	cd - || exit
	progress_log "Completed schedules-export.go"
	printf "\n============================ COMPLETED schedules-exporter ==================\n\n"
}

run_validate() {
	cd golang || exit
	go run cmd/validate-intermediate/validate-intermediate.go "${data_transitional_dir}" || exit $?
	cd - || exit
}

run_timeslice_export() {
	printf "\n============================ RUN multi-period schedules-exporter ==================\n"
	printf "Run timeslice-schedules-export.go (Create final BIN files)\n"
	printf "... from feeds/transitional_data/Px to $data_output_dir/Px\n"
	timeslice_export_prog=cmd/timeslice-schedules-export/timeslice-schedules-export

	progress_log "timeslice-schedules-export.go"
	cd golang || exit
	echo "Building ${timeslice_export_prog}"
	go build -a -o "${timeslice_export_prog}" cmd/timeslice-schedules-export/*.go
	echo "Building schedules-export.go"
	go build -a -o "${export_prog}" cmd/schedules-export/*.go

	echo "Running ${timeslice_export_prog}"
	"${timeslice_export_prog}" \
		--input-dir="${data_transitional_dir}" \
		--output-dir="${data_output_dir}" \
		--sched-prog="${export_prog}" \
		--time-slice-json="${time_slice_json}" \
		--verbose=false
	echo "DONE Running ${timeslice_export_prog}"

	ls -l "${data_output_dir}"/*
	cd - || exit
	progress_log "Completed timeslice-schedules-export.go"
	printf "\n============================ COMPLETED timeslice-schedules-export ==================\n\n"
}

run_load_mongo() {
	printf "\n============================ RUN MongoDB Load ==================\n\n"
	schedulesFile=$(ls -1 /feeds/transitional_data/schedules*.bson | head -1)
	locationsFile=$(ls -1 /feeds/transitional_data/locations*.bson | head -1)
	progress_log "mongorestore file ${schedulesFile} to schedules.schedules in DB: ${mongodb}"
	mongorestore -v --drop --db=schedules --collection=schedules "${mongodb}" "${schedulesFile}"
	progress_log "mongorestore file ${locationsFile} to places.locations in DB: ${mongodb}"
	mongorestore -v --drop --db=places --collection=locations "${mongodb}" "${locationsFile}"
}

run_start_timeslice_planner() {
	printf "\n============================ RUN timeslice-planner as a background task ==================\n\n"
	if [ -n "${time_slice_json}" ]; then
		time_slice_json="/feeds/test_data/time-slice.json"
		echo "No time_slice_json defined, using ${time_slice_json}"
	fi
	printf "=== time slice JSON file is: ${time_slice_json} ===\n"
	run_kill_planner
	export PROTO_DIR="${data_output_dir}"
	cd golang || exit
	echo "Building timeslice-planner.go and planner.go"
	go build -o cmd/timeslice-planner/timeslice-planner cmd/timeslice-planner/*.go
	go build -o cmd/planner/planner cmd/planner/*.go
	cmd/timeslice-planner/timeslice-planner \
		--time-slice-json "${time_slice_json}" \
		--bin-dir="${data_output_dir}" \
		--verbose=true \
		--start-planners=true &

	planner_pid=$!
	cd - || exit
	progress_log "timeslice-planner running as a background task (pid is $planner_pid) and loading data from ${PROTO_DIR}"
	printf "\n============== planner running as a background task pid is ${planner_pid}  ==========\n\n"
	sleep 6

}

run_start_single_planner() {
	printf "\n======================== RUN 'classic' planner (single instance) as a background task ==============\n\n"
	run_kill_planner
	export PROTO_DIR="${data_output_dir}"
	cd golang || exit
	echo "Building  planner.go"
	go build -o cmd/planner/planner cmd/planner/*.go
	cmd/planner/planner serve &

	planner_pid=$!
	cd - || exit
	progress_log "Classic planner running as a background task (pid is $planner_pid) and loading data from ${PROTO_DIR}"
	printf "\n============== Classic planner running as a background task pid is ${planner_pid}  ==========\n\n"
}

push_file_to_s3() {
	# Expects $1 is the  file(path) to be sent, $2 is the S3 path
	if [ "$#" -ne 2 ]; then
		printf "push_file_to_s3 requires 2 parameters, the file to be sent and the S3 path to send to, got: {$#} "
		return
	fi

	SEND_FILE="$1"
	S3_PATH="$2"
	if [ ! -f "${SEND_FILE}" ]; then
		progress_log "Results file ${SEND_FILE} not found"
		return
	fi
	progress_log "running:- aws s3 cp ${SEND_FILE} ${S3_PATH}"
	aws s3 cp "${SEND_FILE}" "${S3_PATH}"
	#	echo "Test report on S3 at ${S3_PATH}"
}

_tarup_kg_files() {
	# Just run a '-record' test - now tar the resulting known-good files
	# and send to S3
	get_known_good_filename
	if [ -z "${KNOWN_GOOD_TAR_FILE}" ]; then
		progress_log "NO known-good files for these tests, cannot archive"
		return
	fi
	cd "${known_good_dir}"
	echo "Known good files to be saved to : ${KNOWN_GOOD_TAR_FILE}"
	tar -cvzf known_good.tar.gz ./*.txt
	ls -l
	push_file_to_s3 known_good.tar.gz "${KNOWN_GOOD_TAR_FILE}"
	cd -
}

_download_kg_files() {
	# Fetch the KG files from S3 and expand.
	get_known_good_filename
	if [ -z "${KNOWN_GOOD_TAR_FILE}" ]; then
		progress_log "NO known-good files for these tests, cannot compare"
		return
	fi
	cd "${known_good_dir}"
	rm -rf "${known_good_dir}/*.txt" "${known_good_dir}"/*.gz
	_get_s3_tar_file "${KNOWN_GOOD_TAR_FILE}" "Known Good route files" .
	zipFile="${LAST_TAR_FILE}"
	progress_log "Extracting known-good files:"
	tar -xzvf "${zipFile}"
	cd -
}

_make_reports() {
	# Send reports to S3
	if [ ! -f "${PLANNER_REPORT_FILE}" ]; then
		progress_log "No test report found (${PLANNER_REPORT_FILE})"
		return
	fi

	s3_test_report_path="${s3_logs_path}"results_$(date +"%Y-%m-%dT%H:%M:%S").html
	s3_test_report_csv_path="${s3_logs_path}"results_$(date +"%Y-%m-%dT%H:%M:%S").csv
	s3_test_report_compare_path="${s3_logs_path}"compare_results_$(date +"%Y-%m-%dT%H:%M:%S").txt
	push_file_to_s3 "${PLANNER_REPORT_FILE}" "${s3_test_report_path}"
	push_file_to_s3 "${PLANNER_REPORT_CSV}" "${s3_test_report_csv_path}"
	if [ -f "${COMPARE_REPORT_TXT}" ]; then
		push_file_to_s3 "${COMPARE_REPORT_TXT}" "${s3_test_report_compare_path}"
	fi
	echo "aws s3 ls ${s3_logs_path} :"
	aws s3 ls "${s3_logs_path}"
}

run_planner_tests() {
	# param $1 may be -record or -compare (or null "")
	printf "\n============================ RUN planner_tests options: ${1} ==================\n"
	printf '\t\t(golang/cmd/planner-test-client/planner-test-client.go)\n\n'

	if [ -z "${TEST_YML_FILE}" ]; then
		TEST_YML_FILE=$(find "${test_data_dir}" -maxdepth 1 -name "*.yml")
		echo "No test YML file defined (TEST_YML_FILE not defined), using: ${TEST_YML_FILE}"
	fi
	if [ ! -f "${TEST_YML_FILE}" ]; then
		echo "Test YML file  ${TEST_YML_FILE} NOT found"
		exit 16
	fi
	if [ -z "${HTML_TEMPLATE}" ]; then
		HTML_TEMPLATE=cmd/planner-test-client/planner-test-report.html
		echo "No HTML Template file defined \(HTML_TEMPLATE not defined\), using: ${HTML_TEMPLATE}"
	fi
	if [ -n "$1" ]; then
		test_opts=$1
		printf "planner_test called with option ${test_opts}\n"
		if [ "${test_opts}" = "-compare" ]; then
			echo "... fetching KG files"
			_download_kg_files
		fi
	else
		printf "planner_test called with NO options\n"
		test_opts=""
	fi

	PLANNER_REPORT_FILE="${REPORT_FILE:-/logs/test_report.html}"
	PLANNER_REPORT_CSV="${REPORT_FILE_PDF:-/logs/test_report.csv}"
	COMPARE_REPORT_TXT="${REPORT_FILE_PDF:-/logs/test_report.txt}"
	progress_log "Running the Planner tests, test file is: ${TEST_YML_FILE}, output is ${PLANNER_REPORT_FILE}, MongoDB is ${mongodb}"
	sleep 5 #Wait for planner gRPC server to start

	cd golang || exit
	printf "\nStarting \n"
	echo "Build planner-test-client.go"
	go build -o cmd/planner-test-client/planner-test-client -gcflags "all=-N -l" cmd/planner-test-client/*.go

	TEST_EXIT_CODE=0
	echo " TEST_YML_FILE is ${TEST_YML_FILE}, test_opts: ${test_opts} "
	#do not put quotes around ${test_opts} (else get empty '' which breaks)
	# shellcheck disable=SC2086
	cmd/planner-test-client/planner-test-client ${test_opts} \
		-test-file="${TEST_YML_FILE}" \
		-log-file="${PLANNER_REPORT_FILE}" \
		-mongodb="${mongodb}" \
		-html-template="${HTML_TEMPLATE}" \
		-plannerAddr="${plannerAddr:-localhost:50053}" ||
		TEST_EXIT_CODE=$?

	cd - || exit
	progress_log "Tests complete, exit code is $TEST_EXIT_CODE"

	_make_reports

	if [ "${TEST_EXIT_CODE}" -ne 0 ]; then
		_send_slack_message "planner-test-client.go FAILED exit code ${TEST_EXIT_CODE} (results in ${s3_test_report_path})"
	else
		_send_slack_message "planner-test-client.go PASSED results in ${s3_test_report_path}"
		# shellcheck disable=SC1073
		# shellcheck disable=SC1072
		if [ "${test_opts}" = "-record" ]; then
			_tarup_kg_files
		elif [ "${test_opts}" = "-compare" ]; then
			printf "Known Good Compare done - report in ${s3_test_report_compare_path}"
		fi
	fi

	printf "\n"
}

_send_slack_message() {
	if [ -z "${SLACK_URI}" ]; then
		progress_log "_send_slack_message Env Var SLACK_URI not defined, must contain Slack app URI"
		return
	fi
	if [ -z "$1" ]; then
		progress_log "_send_slack_message No message \($1 is empty\)"
		return
	fi
	progress_log "send Slack message: $1"

	curl -X POST -H 'Content-type: application/json' \
		--data "{\"text\":\"$1\"}" "${SLACK_URI}"
	printf "\n_send_slack_message DONE \n"
}

_kill_children() {
	sp=$(pgrep -P $$ || true)
	if [ -n "${sp}" ]; then
		echo "Sub processes are: ${sp}"
	fi
	for p in $(pgrep -P $$); do
		echo Killing PID "$p"
		kill -9 "$p"
	done
}

run_kill_planner() {
	# shellcheck disable=SC2009
	planner_pid=$(ps | grep planner | xargs | cut -d " " -f1)
	if [ -z "${planner_pid}" ]; then
		echo NO planner processes running
		return
	fi
	echo "Kill any planner processes: ${planner_pid}"
	pgrep planner
	kill -9 "${planner_pid}" || true
	echo "Kill any planner sub-processes"
	# shellcheck disable=SC2006
	# shellcheck disable=SC2009
	subprocesses=$(ps -ax | grep "planner serve" | grep -v "grep" | awk '{$1=$1};1' | cut -d" " -f 1)
	if [ -n "${subprocesses}" ]; then
		echo "Deleting Planner subprocesses : ${subprocesses}"
		# shellcheck disable=SC2009
		ps -ax | grep "planner serve" | grep -v "grep" | awk '{$1=$1};1' | cut -d" " -f 1 | xargs kill -9
	else
		echo "No Planner subprocesses"
	fi
	pgrep planner
}

run_tests() {
	# Runs the tests using existing data - timeslice version
	# see also run_tests_classic
	# takes one optional parameter -compare or -record (leave blank for basic tests only)
	printf "\nEnd to End TimeSlice Schedules tests only, starting at $(date)\n"
	echo "Test type is : $1 (blank means basic tests only)"
	progress_log "Start planner and run tests only"
	run_fetch_test_data

	run_start_timeslice_planner

	run_planner_tests "$1"
	progress_log "End to End TimeSlice Schedules data processing, ALL DONE at $(date)"
}

run_tests_classic() {
	# Runs the tests using existing data - classic version (single planner instance)
	# see also run_tests
	# takes one optional parameter -compare or -record
	printf "\nEnd to End Classic Schedules tests only, starting at $(date)\n"
	echo "Test type is : $1 (blank means basic tests only)"
	run_fetch_test_data
	unset time_slice_json
	run_start_single_planner
	run_planner_tests "$1"
	progress_log "End to End Classic Schedules data processing, ALL DONE at $(date)"
}

#</editor-fold>

## MAIN()

run_all_timeslice() {
	# param $1 may be -record or -compare (or null "")

	progress_log "bash/e2e.sh STARTING"
	printf "\nEnd to End Schedules data processing, with parameters: $*, starting at $(date)\n"

	run_fetch_test_data

	run_import

	run_timeslice_export

	run_load_mongo

	run_start_timeslice_planner

	run_planner_tests "$1"

	progress_log "End to End Schedules data processing, ALL DONE at $(date)"
}

run_all_classic() {
	progress_log "bash/e2e.sh STARTING"
	printf "\nEnd to End Classic Schedules data processing, starting at $(date)\n"

	run_fetch_test_data

	unset time_slice_json

	run_import

	run_validate

	run_export

	run_load_mongo

	run_start_single_planner

	run_planner_tests "$1"

	progress_log "End to End Classic Schedules data processing, ALL DONE at $(date)"
}

run_hub_dev_server() {
	printf "\n============================ STARTING Development Server (Junction Hub) ==================\n"
	# Navigate to hub-web repository
	cd svelte/hub-web || exit
	# Start the development server in the background
	printf "Starting development server...\n"
	yarn run dev &
	# Store the server's process ID so we can stop it later
	SERVER_PID=$!
	# Wait a little for the server to start up
	sleep 10 # Adjust this based on how long your server takes to start
	# Go back to the original directory
	cd - || exit
	printf "Development server started with PID: $SERVER_PID\n"
	printf "\n============================ Development Server (Junction Hub) RUNNING ==================\n\n"
}

run_hub_onewaytrip_tests() {
	printf "\n============================ RUN Onewaytrip Tests ==================\n"

	run_hub_dev_server

	# Execute the onewaytrip end-to-end test
	printf "Executing onewaytrip end-to-end test...\n"
	npx playwright test svelte/hub-web/e2e-tests/tests/onewaytrip.spec.ts --config svelte/hub-web/playwright.config.ts

	# Stop any servers or services started specifically for this test
	if [ -n "$SERVER_PID" ]; then
		printf "Stopping development server...\n"
		kill "$SERVER_PID"
	fi

	printf "\n============================ COMPLETED Onewaytrip Tests ==================\n\n"
}

run_hub_roundtrip_tests() {
	printf "\n============================ RUN Roundtrip Tests ==================\n"
	# Start the development server for junction hub
	run_hub_dev_server

	printf "Executing roundtrip end-to-end tests...\n"
	npx playwright test svelte/hub-web/e2e-tests/tests/roundtrip.spec.ts --config svelte/hub-web/playwright.config.ts

	# After tests completion, kill the development server
	if [ -n "$SERVER_PID" ]; then
		printf "Stopping development server...\n"
		kill "$SERVER_PID"
	fi

	printf "\n============================ COMPLETED Roundtrip Tests ==================\n\n"
}

# Script MAIN starts HERE

run_startup

if [ "$#" -eq 0 ]; then
	printf ">> NO parameters specified, running ALL (0)\n"
	if [ "$#" -gt 0 ]; then
		shift
	fi
	run_all_timeslice "$@"
	_kill_children
	exit
fi
# Any parameters are function names, or are ignored

var=$1
if [ "$var" == "list" ]; then
	printf ">> List of available functions\n"
	declare -F | grep run_
	exit 0
else
	if [[ $(type -t "$var") == function ]]; then
		printf ">> Calling function $var\n"
		shift
		$var "$@"
		printf "\n>> Completed function $var\n"
	else
		printf ">> No such function: $var\n"
	fi
fi

printf "\n==========================  run_e2e_tests.sh  ALL DONE ===============================\n\n"
exit
