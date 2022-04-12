#!/usr/bin/env bash
set -eu

root_dir="$(CDPATH='' cd -- "$(dirname -- "$0")/.." && pwd)"

wait_for_port() {
	echo "* Waiting for ${1}:${2} to respond..."

	while ! nc -z "${1}" "${2}" 1>/dev/null 2>/dev/null; do
		sleep 0.1
	done
}

start_third_party() {
	echo "* Starting third-party services..."
	docker compose -f "${root_dir}/docker-compose.yml" -p junction up -d 1>/dev/null 2>/dev/null &

	wait_for_port localhost 5672
	wait_for_port localhost 6379
	wait_for_port localhost 27017
}

generate_dataset() {
	trap 'kill 0' EXIT

	"${root_dir}/bash/run.sh" "${root_dir}/python/snowfall/service/geodata/main.py" grpc 1>/dev/null 2>/dev/null &

	wait_for_port localhost 50058

	"${root_dir}/bash/run.sh" "${root_dir}/python/snowfall/junction/places/main.py" import 1>/dev/null 2>/dev/null &
	"${root_dir}/bash/run.sh" "${root_dir}/python/snowfall/junction/schedules/main.py" import 1>/dev/null 2>/dev/null &
	"${root_dir}/bash/run.sh" "${root_dir}/python/snowfall/junction/gtfs_feed/main.py" import 1>/dev/null 2>/dev/null &
	GTFS_FEED_IMPORT_PID="$!"

	echo "* Importing GTFS feed..."

	wait "${GTFS_FEED_IMPORT_PID}"

	echo "* Exporting optimized schedules..."

	"${root_dir}/bash/run.sh" "${root_dir}/python/snowfall/junction/schedules/main.py" export 1>/dev/null 2>/dev/null &
	SCHEDULES_EXPORT_PID="$!"

	wait "${SCHEDULES_EXPORT_PID}"
}

start_third_party
generate_dataset
