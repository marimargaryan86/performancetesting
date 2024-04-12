#!/bin/bash
PACKAGE="models"

xsdata wsdls/shopping.wsdl --package $PACKAGE --structure-style filenames
rm models/__init__.py

grep -Rohli "^\(\s*@dataclass\)\s*$" models/ | xargs -r -L 1 sed -i -e "s/^\(\s*@dataclass\)\s*$/\1(frozen=True)/i"

pants fix models/

# The shopping WSDL file produces a nested StatusMessages class that inherit a top-level StatusMessages class.
# This leads MyPy to detect a cyclic dependency, so we add ignore hints to silence it.
grep -Rohli "^\s*class StatusMessages(StatusMessages):\s*$" models/ | xargs -r -L 1 sed -i -e "s/\(^\s*class StatusMessages(StatusMessages):\s*$\)/\1  # type: ignore[misc]/i"
grep -Rohli "^\s*status_messages: Optional\[\"RequestStatusType\.StatusMessages\"\] =" models/ | xargs -r -L 1 sed -i -e "s/\(^\s*status_messages: Optional\[\"RequestStatusType.StatusMessages\"\] =.*$\)/\1  # type: ignore[misc]/i"
