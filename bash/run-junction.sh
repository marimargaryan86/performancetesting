#!/usr/bin/env bash
set -eu

root_dir="$(CDPATH='' cd -- "$(dirname -- "$0")/.." && pwd)"

wait_for_port() {
	echo "* Waiting for ${1}:${2} to respond..."
	nc -w 10 -z "${1}" "${2}" 1>/dev/null 2>/dev/null
}

start_third_party() {
	echo "* Starting third-party services..."
	docker compose -f "${root_dir}/docker-compose.yml" -p junction up -d 1>/dev/null 2>/dev/null &

	wait_for_port localhost 5672
	wait_for_port localhost 6379
	wait_for_port localhost 27017
}

interrupt_handler() {
	for pid in "$@"; do
		echo "* Interrupting process ${pid}..."
		kill -INT "${pid}"
	done
}

generate_dataset() {
	"${root_dir}/bash/run.sh" "${root_dir}/python/snowfall/service/geodata/main.py" grpc 1>/dev/null 2>/dev/null &
	GEODATA_GRPC_PID="$!"

	wait_for_port localhost 50058

	"${root_dir}/bash/run.sh" "${root_dir}/python/snowfall/junction/places/main.py" import 1>/dev/null 2>/dev/null &
	PLACES_IMPORT_PID="$!"
	"${root_dir}/bash/run.sh" "${root_dir}/python/snowfall/junction/schedules/main.py" import 1>/dev/null 2>/dev/null &
	SCHEDULES_IMPORT_PID="$!"
	"${root_dir}/bash/run.sh" "${root_dir}/python/snowfall/junction/gtfs_feed/main.py" import 1>/dev/null 2>/dev/null &
	GTFS_FEED_IMPORT_PID="$!"

	echo "* Importing GTFS feed..."

	trap 'interrupt_handler "${PLACES_IMPORT_PID}" "${SCHEDULES_IMPORT_PID}" "${GTFS_FEED_IMPORT_PID}" "${GEODATA_GRPC_PID}"' INT
	wait "${GTFS_FEED_IMPORT_PID}"
	kill -INT "${PLACES_IMPORT_PID}"
	kill -INT "${SCHEDULES_IMPORT_PID}"
	kill -INT "${GEODATA_GRPC_PID}"

	echo "* Exporting optimized schedules..."

	"${root_dir}/bash/run.sh" "${root_dir}python/snowfall/junction/schedules/main.py" export 1>/dev/null 2>/dev/null &
	SCHEDULES_EXPORT_PID="$!"

	trap 'interrupt_handler "${SCHEDULES_EXPORT_PID}"' INT
	wait "${SCHEDULES_EXPORT_PID}"
}

start_third_party
generate_dataset
