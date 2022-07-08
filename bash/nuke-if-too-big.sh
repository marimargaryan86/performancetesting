#!/usr/bin/env bash
set -eu

function nuke_if_too_big() {
	path=$1

	if [[ ! -d "$path" ]]; then
		echo "${path} does not exist, skipping it."
		return
	fi

	limit_mb=$2
	size_mb=$(du -m -d0 "${path}" | cut -f 1)
	if ((size_mb > limit_mb)); then
		echo "${path} is larger than ${limit_mb}mb (currently at ${size_mb}mb), nuking it."
		rm -rf "${path:?}"/*
	else
		echo "${path} is smaller than ${limit_mb}mb (currently at ${size_mb}mb), keeping it."
	fi
}

nuke_if_too_big "$1" "$2"
