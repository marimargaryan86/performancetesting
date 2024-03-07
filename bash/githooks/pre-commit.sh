#!/usr/bin/env bash
set -e

COLOR_RED="\x1b[31m"
COLOR_RESET="\x1b[0m"

function log() {
	echo -e "$@" 1>&2
}

function die() {
	(($# > 0)) && log "\n${COLOR_RED}$*${COLOR_RESET}"
	exit 1
}

function git_merge_base() {
	git rev-parse --symbolic-full-name --abbrev-ref HEAD@\{upstream\} 2>/dev/null || git rev-parse HEAD^
}

if [[ -n "${GIT_DIR}" && "${GIT_DIR}" != /* ]]; then
	GIT_DIR="$(pwd)/${GIT_DIR}"
	export GIT_DIR
fi

MERGE_BASE="$(git_merge_base)"

echo "* Typechecking"
pants --changed-since="${MERGE_BASE}" --changed-dependents=transitive check

echo "* Checking linters, and formatters"
pants --changed-since="${MERGE_BASE}" lint ||
	die "If there were formatting errors, run \`pants --changed-since=$(git rev-parse --symbolic "${MERGE_BASE}") fix\`"
