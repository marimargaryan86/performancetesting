# Silverrail Client API

This is a thin wrapper on top of [Silverrail](https://silverrailtech.com/) SOAP
API. Silverrail is a rail distribution platform that offer search and booking
capabilities across several train operators in Europe.

The API docs are available [here](https://docs.silverrailtech.com/docs). They
require an account, but Silverrail has set it up so that any snowfalltravel.com
email have access to it, so you can just sign up with your work email.

## Generating Models

Silverrail provides WSDL and XSD files that we have downloaded from their documentation
and checked in under `wsdls/`.  The `models/` are auto-generated from the WSDL
files by running:

    ./generate-models.sh

This was done once and checked in, so the script is mostly present for
documentation on how to reproduce this, in particular there are a few fixes to
apply to the generated code to make it fit some of our CI/CD rules.

> In the case of `wsdls/stations.xsd`, only models of resources are generated. Request and response `Body` models are not auto-generated.
> They are added manually to the `models/stations.py`. Be cautious to not remove them by regenerating the file.

## Authentication

Silverrail will provide a [`.pfx`](https://en.wikipedia.org/wiki/PKCS_12) file
containing our SSL certificate (both our private key and our certificate with
the public key). They will also provide us with a password that can decrypt
this file, we can use it to generate both files and then store them in Vault to
pass them at runtime to the API client.

## How to use

A minimal driver code that performs a simple search query is shown below.

```python

import asyncio
import httpx
from tempfile import NamedTemporaryFile

from snowfall.vendor.silverrail.client import ( SilverrailClient, SilverrailSettings)
from snowfall.vendor.silverrail.models.shopping import (
    PointToPointShoppingQuery,
    QueryTravelPointPairType,
    TravelPointType,
    DateTimeWindowType,
)

# TODO: Inline the certificate file.
CERT_STR = """
-----BEGIN CERTIFICATE-----
...
-----END CERTIFICATE-----
"""

# TODO: Inline the private key file.
PRIVATE_KEY_STR = """
-----BEGIN PRIVATE KEY-----
...
-----END PRIVATE KEY-----
"""

settings = SilverrailSettings(distributor_code='SNOWFALL', pos_code='FR', channel_code='WEB')

query = PointToPointShoppingQuery(
                travel_point_pairs=PointToPointShoppingQuery.TravelPointPairs(
                    travel_point_pair=[
                        QueryTravelPointPairType(
                            origin_travel_point=TravelPointType(
                                value="FRLYS",
                                type_value="STATION",
                            ),
                            destination_travel_point=TravelPointType(
                                value="FRXYD",
                                type_value="STATION",
                            ),
                            departure_date_time_window=DateTimeWindowType(
                                date="2024-06-29",
                                time="10:00:00"
                            )
                        )
                    ]
                ),
                passenger_specs=PointToPointShoppingQuery.PassengerSpecs(
                    passenger_spec=[
                        PointToPointShoppingQuery.PassengerSpecs.PassengerSpec(
                            passenger_spec_id="PAX_A1",
                            age=40,
                        )
                    ]
                )
            )


async def run() -> None:
    with NamedTemporaryFile(mode='w+b') as cert_file, NamedTemporaryFile(mode='w+b') as key_file:
        cert_file.write(CERT_STR.encode('utf-8')); cert_file.seek(0)
        key_file.write(PRIVATE_KEY_STR.encode('utf-8'));  key_file.seek(0)

        http_client = httpx.AsyncClient(
            http2=True,
            cert=( cert_file.name, key_file.name),
        )

        client = SilverrailClient(base_url="https://xml-cert-nex.railgds.net", settings=settings, http_client=http_client)
        return await client.shopping_point_to_point(query)

print(asyncio.run(run()))
```

Make sure to replace the `CERT_STR` and the `PRIVATE_KEY_STR` with the
certificate and private key (in plain text) that identify our Snowfall account
with Silverrail. If you copy this code in a file `test.py`, you can then execute
it with `pants run test.py`.
