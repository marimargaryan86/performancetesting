#!/usr/bin/env bash
set -eu

root_dir="$(CDPATH='' cd -- "$(dirname -- "$0")/.." && pwd)"

start_third_party() {
	echo "* Starting third-party services..."
	docker compose -f "${root_dir}/docker-compose.yml" -p junction up -d 1>/dev/null 2>/dev/null &
}

generate_dataset() {
	echo "* Importing GTFS feed..."

	"${root_dir}/bash/run.sh" "${root_dir}/python/snowfall/service/geodata/main.py" grpc 1>/dev/null 2>/dev/null &
	GEODATA_GRPC_PID="$!"
	"${root_dir}/bash/run.sh" "${root_dir}/python/snowfall/junction/places/main.py" import 1>/dev/null 2>/dev/null &
	PLACES_IMPORT_PID="$!"
	"${root_dir}/bash/run.sh" "${root_dir}/python/snowfall/junction/schedules/main.py" import 1>/dev/null 2>/dev/null &
	SCHEDULES_IMPORT_PID="$!"

	"${root_dir}/bash/run.sh" "${root_dir}/python/snowfall/junction/gtfs_feed/main.py" import 1>/dev/null 2>/dev/null &
	GTFS_FEED_IMPORT_PID="$!"

	wait "${GTFS_FEED_IMPORT_PID}"
	kill -INT "${PLACES_IMPORT_PID}"
	kill -INT "${SCHEDULES_IMPORT_PID}"
	kill -INT "${GEODATA_GRPC_PID}"

	echo "* Exporting optimized schedules..."

	"${root_dir}/bash/run.sh" "${root_dir}python/snowfall/junction/schedules/main.py" export 1>/dev/null 2>/dev/null &
	SCHEDULES_EXPORT_PID="$!"

	wait "${SCHEDULES_EXPORT_PID}"
}

start_third_party
generate_dataset
