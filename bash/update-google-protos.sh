#!/usr/bin/env bash
set -eu

root_dir="$(CDPATH='' cd -- "$(dirname -- "$0")/.." && pwd)"
filenames=("datetime.proto" "latlng.proto")
base_path="${root_dir}/protobuf/snowfall/common/v1alpha"

mkdir -p "${base_path}"

for f in "${filenames[@]}"; do
	filepath="${base_path}/${f}"
	echo "${filepath}"
	curl --silent "https://raw.githubusercontent.com/googleapis/googleapis/master/google/type/${f}" >"${filepath}"
	sed "/^option /d" "${filepath}" | sponge "${filepath}"
	sed "s/package google.type;/package snowfall.common.v1alpha;/g" "${filepath}" | sponge "${filepath}"
	"${root_dir}/pants" fmt "${filepath}"
	ex "${filepath}" <<eof
14 insert
//
// Modifications by Snowfall Ltd:
// - changed package to \`snowfall.common.v1alpha\`
// - formatted with \`buf format\`
.
xit
eof
done
