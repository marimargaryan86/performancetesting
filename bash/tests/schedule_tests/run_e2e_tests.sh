#!/bin/bash
# tests/schedule_tests/run_e2e_tests.sh
# shellcheck disable=SC2012  # using ls to find most recent file
# shellcheck disable=SC2059  # variables in printf are fine
# End to End script
# If run with no options, it runs function `run_all`
# Run `run_e2e_tests.sh list` to see available functions
# Requires these external env vars:
# E2E_TEST_YML_FILE, the full S3 path to a test YML file

data_root="${E2E_DATA_ROOT:-$HOME/feeds}"
test_root="bash/tests/schedule_tests"
data_input_dir="${data_root}"/input_data/
data_transitional_dir="${data_root}"/transitional_data
known_good_dir="${data_root}"/known_good/
audit_dir="${data_root}"/logs
data_output_dir="${data_root}"/output_data
logs_dir="${data_root}"/logs
progress_log_file="${data_root}"/logs/progress_$(date +"%Y-%m-%dT%H:%M:%S").log
time_slice_json=cmd/gtfs-import/time-slice.json
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
	#	TODO make sure all steps call progress_logs
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
	progress_log "Run startup All OK"
}

run_import() {
	printf "\n============================ RUN gtfs-import ==================\n"
	progress_log "Run Import (All GTFS files) from feeds/input_data to feeds/transitional_data"
	# eg import from feeds/input_data/*.zip to feeds/transitional_data/ BIN files.
	cd golang || exit # TODO delete, not needed with Pants
	mkdir -p "${data_transitional_dir}"
	rm -f "${data_transitional_dir}"/*.bin "${data_transitional_dir}"/*.bson
	time_slice_json=golang/cmd/gtfs-import/time-slice.json
	echo "Building gtfs-import.go (with timeslice file ${time_slice_json})"

	if [ -z "$RUN_DATE" ]; then
		printf "============= without RUN_DATE set  =============\n\n"
		pants run golang/cmd/gtfs-import/:bin -- \
			--input-dir="${data_input_dir}" \
			--output-dir="${data_transitional_dir}" \
			--time-slice-json="${time_slice_json}"
	else
		printf "============= with RUN_DATE: ${RUN_DATE} =============\n\n"
		pants run golang/cmd/gtfs-import/:bin -- \
			--input-dir="${data_input_dir}" \
			--output-dir="${data_transitional_dir}" \
			--run-date="${RUN_DATE}" \
			--time-slice-json="${time_slice_json}"

	fi
	cd - || exit
	ls -l "${data_transitional_dir}"
	file_count=$(ls -1q "${data_transitional_dir}" | wc -l)
	if [ "${file_count}" -eq "0" ]; then
		progress_log "ERROR from gtfs-import.go NO FILES in ${data_transitional_dir}"
		exit 22
	fi
	progress_log "Completed gtfs-import.go"
	printf "\n============================ COMPLETED gtfs-import ==================\n\n"

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
	progress_log "Downloading $2 TAR file  ${tar_file_s3} - > ${target_dir}"
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
	progress_log "Downloaded $2 TAR file to: ${target_dir}/${tar_file}"
	LAST_TAR_FILE="${target_dir}/${tar_file}"
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
	progress_log "Fetch test data file  ${E2E_TEST_YML_FILE} from S3: to test input at ${data_input_dir}"
	rm -rf "${data_input_dir}"
	if ! aws s3 cp "${E2E_TEST_YML_FILE}" "${data_input_dir}"; then
		echo aws s3 cp "${E2E_TEST_YML_FILE}" failed
		exit 11
	fi
	TEST_YML_FILE=$(find "${data_input_dir}" -maxdepth 1 -name "*.yml")
	if [ -z "${TEST_YML_FILE}" ]; then
		echo Missing test file in "${data_input_dir}"
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

	printf "\n============================ FETCH TEST DATA COMPLETE ==================\n\n"
}

get_known_good_filename() {
	# get KG filename from test.yml, sets into KNOWN_GOOD_TAR_FILE
	TEST_YML_FILE=$(find "${data_input_dir}" -maxdepth 1 -name "*.yml")
	if [ -z "${TEST_YML_FILE}" ]; then
		echo Missing test file in "${data_input_dir}"
		exit 22
	fi
	KNOWN_GOOD_TAR_FILE=$(yq '."test-details"."known-good-files"' "${TEST_YML_FILE}" | tr -d '"')
	# Note returns literal string "null" if no file!
	if [ -z "${KNOWN_GOOD_TAR_FILE}" ] || [ "${KNOWN_GOOD_TAR_FILE}" == "null" ]; then
		progress_log "NO known-good files for these tests"
		unset KNOWN_GOOD_TAR_FILE
	else
		progress_log "KNOWN_GOOD_TAR_FILE for these tests is ${KNOWN_GOOD_TAR_FILE}"
	fi
}

run_export() {
	printf "\n============================ RUN schedules-exporter ==================\n"
	printf "Run schedules-exporter.go \(Create final BIN files\)\n"
	printf "... from feeds/transitional_data to $data_output_dir\n"

	progress_log "Run schedules-export.go"
	rm -rf "${data_output_dir}"
	mkdir -pv "${data_output_dir}"
	cd golang || exit
	echo "Building schedules-export.go "
	pants run golang/cmd/schedules-export/:bin -- --input-dir="${data_transitional_dir}" --output-dir="${data_output_dir}"
	ls -l "${data_output_dir}"
	cd - || exit
	progress_log "Completed schedules-export.go"
	printf "\n============================ COMPLETED schedules-exporter ==================\n\n"
}

if [ -f "noway.no" ]; then
	run_export
	# TODO xxxxx delete, and delete run_export one day
fi

run_timeslice_export() {
	printf "\n============================ RUN multi-period schedules-exporter ==================\n"
	printf "Run timeslice-schedules-export.go \(Create final BIN files\)\n"
	printf "... from feeds/transitional_data/Px to $data_output_dir/Px\n"

	progress_log "timeslice-schedules-export.go"
	cd golang || exit
	echo "Building timeslice-schedules-export "
	echo "Building schedules-export.go "
	export_prog=dist/golang.cmd.schedules-export/bin

	echo "Running timeslice-schedules-export"
	pants run golang/cmd/timeslice-schedules-export:bin -- \
		--input-dir="${data_transitional_dir}" \
		--output-dir="${data_output_dir}" \
		--sched-prog="${export_prog}" \
		--time-slice-json="${time_slice_json}" \
		--verbose=false
	echo "DONE Running timeslice-schedules-export"

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

run_start_planner() {
	printf "\n============================ RUN planner as a background task ==================\n\n"
	run_kill_planner
	export PROTO_DIR="${data_output_dir}"
	cd golang || exit
	echo "Building planner.go "
	dist/golang.cmd.planner/bin serve &
	planner_pid=$!
	cd - || exit
	progress_log "planner running as a background task \(pid is $planner_pid\) and loading data from ${PROTO_DIR}"
	printf "\n============== planner running as a background task pid is ${planner_pid}  ==========\n\n"
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

run_planner_types() {
	# Alters the test run depending on KG_RUN_TYPE.
	# If unset or "", no KG is run
	run_planner_tests "${KG_RUN_TYPE}"
}

# shellcheck disable=SC2317
run_planner_record() {
	printf "\n============================ RUN planner_tests with -record ==================\n"
	run_planner_tests -record
}

# shellcheck disable=SC2317
run_planner_compare() {
	printf "\n============================ RUN planner_tests with -compare ==================\n"
	run_planner_tests -compare
}

_make_reports() {
	# Send reports to S3
	if [ ! -f "${PLANNER_REPORT_FILE}" ]; then
		progress_log "No test report found (${PLANNER_REPORT_FILE})"
		return
	fi

	weasyprint "${PLANNER_REPORT_FILE}" "${PLANNER_REPORT_PDF}"
	printf "PDF report created: ${PLANNER_REPORT_PDF}\n"
	s3_test_report_path="${s3_logs_path}"results_$(date +"%Y-%m-%dT%H:%M:%S").html
	s3_test_report_pdf_path="${s3_logs_path}"results_$(date +"%Y-%m-%dT%H:%M:%S").pdf
	s3_test_report_compare_path="${s3_logs_path}"compare_results_$(date +"%Y-%m-%dT%H:%M:%S").txt
	push_file_to_s3 "${PLANNER_REPORT_FILE}" "${s3_test_report_path}"
	push_file_to_s3 "${PLANNER_REPORT_PDF}" "${s3_test_report_pdf_path}"
	if [ -f "${COMPARE_REPORT_TXT}" ]; then
		push_file_to_s3 "${COMPARE_REPORT_TXT}" "${s3_test_report_compare_path}"
	fi
	echo "aws s3 ls ${s3_logs_path} :"
	aws s3 ls "${s3_logs_path}"

}
run_planner_tests() {
	# param $1 may be -record or -compare (or null "")
	printf "\n============================ RUN planner_tests options ${1} ==================\n"
	printf '\t\t(golang/cmd/planner-test-client/planner-test-client.go)\n\n'
	if [ -z "${TEST_YML_FILE}" ]; then
		TEST_YML_FILE=$(find "${data_input_dir}" -maxdepth 1 -name "*.yml")
		echo "No test YML file defined \(TEST_YML_FILE not defined\), using: ${TEST_YML_FILE}"
	fi
	if [ ! -f "${TEST_YML_FILE}" ]; then
		echo "Test YML file  ${TEST_YML_FILE} NOT found"
		exit 16
	fi
	if [ -z "${HTML_TEMPLATE}" ]; then
		HTML_TEMPLATE=./planner-test-report.html
		echo "No HTML Template file defined \(HTML_TEMPLATE not defined\), using: ${HTML_TEMPLATE}"
	fi
	if [ -n "$1" ]; then
		test_opts=$1
		printf "planner_test called with option ${test_opts}\n"
		if [ "${test_opts}" = "-compare" ]; then
			_download_kg_files
		fi
	else
		printf "planner_test called with NO options\n"
		test_opts=""
	fi

	PLANNER_REPORT_FILE="${REPORT_FILE:-/logs/test_report.html}"
	PLANNER_REPORT_PDF="${REPORT_FILE_PDF:-/logs/test_report.pdf}"
	COMPARE_REPORT_TXT="${REPORT_FILE_PDF:-/logs/test_report.txt}"
	progress_log "Running the Planner tests, test file is: ${TEST_YML_FILE}, output is ${PLANNER_REPORT_FILE}, MongoDB is ${mongodb}"
	sleep 5 #Wait for planner gRPC server to start

	cd golang || exit
	printf "\nStarting \n"
	echo "Build planner-test-client.go "

	TEST_EXIT_CODE=0
	pants run golang/cmd/planner-test-client:bin -- "${test_opts}" \
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
		_send_slack_message "planner-test-client.go FAILED exit code ${TEST_EXIT_CODE}"
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

exit_if_not_junction() {
	# Exits if not in Junction repo root and if some key directories are missing

	if [ ! -d "${test_root}" ]; then
		echo "Test directory ${test_root} not in the repo root"
		progress_log "exit_if_not_junction FAILED, exiting"
		exit 1
	fi
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
	# Only works on one planner!
	# shellcheck disable=SC2009
	planner_pid=$(ps | grep planner | xargs | cut -d " " -f1)
	if [ -z "${planner_pid}" ]; then
		echo NO planner processes running
		return
	fi
	echo "Kill any planner processes: ${planner_pid}"
	# shellcheck disable=SC2317
	pgrep planner
	# shellcheck disable=SC2317
	kill -9 "${planner_pid}" || true
	# shellcheck disable=SC2317
	pgrep planner
}

#</editor-fold>

## MAIN
run_all() {
	progress_log "bash/e2e.sh STARTING"
	printf "\nEnd to End Schedules data processing, starting at $(date)\n"

	exit_if_not_junction

	run_fetch_test_data

	run_import

	run_timeslice_export

	run_load_mongo

	run_start_planner

	run_planner_types

	progress_log "End to End Schedules data processing, ALL DONE at $(date)"
}

_prep_tests() {
	# OFFS some checkers are very dumb
	# shellcheck disable=SC2317
	echo "KG_RUN_TYPE is : ${KG_RUN_TYPE}"
	# shellcheck disable=SC2317
	progress_log "Start planner and run tests only"
	# shellcheck disable=SC2317
	run_start_planner
	# shellcheck disable=SC2317
	run_fetch_test_data
}
run_tests() {
	# Runs the tests using existing data
	# OFFS some checkers are very dumb
	# shellcheck disable=SC2317
	_prep_tests
	# shellcheck disable=SC2317
	run_planner_types
}

run_record() {
	# Runs the tests with -recordusing existing data
	# OFFS some checkers are very dumb
	# shellcheck disable=SC2317
	_prep_tests
	# shellcheck disable=SC2317
	run_planner_tests -record
}

# Script MAIN starts HERE

run_startup
exit_if_not_junction

if [ "$#" -eq 0 ]; then
	printf ">> NO parameters specified, running ALL\n"
	#	printf "\n>> Output saved to ./e2e.log\n"
	run_all
	#	run_all 2>&1 | tee "${logs_dir}"/e2e.log
	_kill_children
	exit
fi
# Any parameters are function names, or are ignored

for var in "$@"; do
	if [ "$var" == "list" ]; then
		printf ">> List of available functions\n"
		declare -F | grep run_
		break
	else
		if [[ $(type -t "$var") == function ]]; then
			printf ">> Calling function $var\n"
			$var
			printf "\n>> Completed function $var\n"
		else
			printf ">> No such function: $var\n"
		fi
		#		printf ">> Function $var COMPLETED\n\n"
	fi
done

printf "\n==========================  run_e2e_tests.sh  ALL DONE ===============================\n\n"
exit
