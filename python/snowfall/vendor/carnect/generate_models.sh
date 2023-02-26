#!/bin/bash
PACKAGE="models"

curl -s -H "Accept-Encoding: gzip" --output - https://ota2007a.carhire-solutions.com/service.asmx?WSDL | gunzip >wsdls/service.wsdl
curl -s -H "Accept-Encoding: gzip" --output - https://ota2007a.micronnexus-staging.com/destination.asmx?WSDL | gunzip >wsdls/destination.wsdl

xsdata wsdls/service.wsdl --package $PACKAGE --structure-style filenames
xsdata wsdls/destination.wsdl --package $PACKAGE --structure-style filenames

rm models/__init__.py

grep -Rohli "^\(\s*class \w\+\):\s*" models/ | xargs -r -L 1 sed -i -e "s/^\(\s*class \w\+\):\s*/\1(object):/i"
# grep -Rohli "^\(\s*@dataclass\)\s*$" models/ | xargs -r -L 1 sed -i -e "s/^\(\s*@dataclass\)\s*$/\1(frozen=True)/i"
pants fix ::
grep -Rohli "^\(\s*object\)\s*$" models/ | xargs -r -L 1 sed -i -e "s/^\(\s*object\)\s*$/\1,/i"
grep -Rohli "^\(\s*VehicleEquipmentCoreType\)\s*$" models/ | xargs -r -L 1 sed -i -e "s/^\(\s*VehicleEquipmentCoreType\)\s*$/\1,/i"
