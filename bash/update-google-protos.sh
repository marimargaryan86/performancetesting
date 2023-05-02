#!/usr/bin/env bash
set -eu

root_dir="$(CDPATH='' cd -- "$(dirname -- "$0")/.." && pwd)"
filenames=("date.proto" "datetime.proto" "latlng.proto" "money.proto" "phone_number.proto" "postal_address.proto")
base_path="${root_dir}/protobuf/snowfall/stdlib/v1alpha"

mkdir -p "${base_path}"

for f in "${filenames[@]}"; do
	filepath="${base_path}/${f}"
	echo "${filepath}"
	curl --silent "https://raw.githubusercontent.com/googleapis/googleapis/master/google/type/${f}" >"${filepath}"
	sed "/^option /d" "${filepath}" | sponge "${filepath}"
	sed "s/package google.type;/package snowfall.stdlib.v1alpha;\\n\\noption go_package = \"git.snowfall.se\/junction\/junction\/golang\/protobuf\/snowfall\/stdlib\/v1alpha\";/g" "${filepath}" | sponge "${filepath}"
	ex "${filepath}" <<eof
14 insert
//
// Modifications by Snowfall Ltd:
// - changed package to \`snowfall.stdlib.v1alpha\`
// - changed option \`go_package\` to \`"git.snowfall.se/junction/junction/golang/protobuf/snowfall/stdlib/v1alpha"\`
// - formatted with \`buf format\`
.
xit
eof
done

pants fix "${base_path}"
