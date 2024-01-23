"""Update local Mongo from dev.

Note: this drops the mentioned collections before restoring them.
"""

import subprocess
import sys
from typing import Any

from pymongo import MongoClient

DUMP_DIR = "/dev-dump"

to_copy = [
    ("trips", "trips"),
    ("places", "locations"),
    ("places", "places"),
]

mock_company = {
    "_id": "db54f5fd-55e9-41f7-8716-09b91e189fe6",
    "name": "MOCK COMPANY",
    "address": {
        "region_code": "SE",
        "postal_code": "29620",
        "locality": "TORREMOLINOS",
        "address_lines": [
            "Centro Cial. Montemar, local 117",
        ],
        "revision": 0,
        "language_code": "",
        "sorting_code": "",
        "administrative_area": "",
        "sublocality": "",
        "recipients": [],
        "organization": "",
    },
    "processing_markup": 5.4,
    "payment_method": 1,
    "payment_type": 1,
    "fx_markup": 0,
    "sales_markup": 0,
    "account_id": "",
    "reseller_markups": [],
    "fee_amounts": [
        {
            "currency_code": "EUR",
            "units": "0",
            "nanos": 0,
        },
    ],
}

mock_reseller = {
    "_id": "d85ac9ee-55f1-4273-8cc8-5e9c9f326b84",
    "name": "MOCK RESELLER",
    "company_id": "db54f5fd-55e9-41f7-8716-09b91e189fe6",
    "default_currency": "EUR",
    "parent_reseller_ids": [],
    "provider_ids": [
        "f9ce75d1-2025-4ab5-b5d7-69e4c14c053e",
    ],
}


class MissingEnvVarError(Exception):
    """When an environment variable is missing."""


def main() -> None:
    if len(sys.argv) < 2:
        sys.stderr.write("Please pass the connection string for dev Mongo.\n")
        sys.exit(1)

    dev_mongo_uri = sys.argv[1]

    upsert_documents()
    restore_from_dump(dev_mongo_uri)


def upsert_documents() -> None:
    client: MongoClient[Any] = MongoClient("mongodb://localhost:27017/")

    companies_db = client["companies"]
    companies_col = companies_db["companies"]
    companies_col.replace_one({"_id": mock_company["_id"]}, mock_company, upsert=True)

    resellers_db = client["resellers"]
    resellers_col = resellers_db["resellers"]
    resellers_col.replace_one({"_id": mock_reseller["_id"]}, mock_reseller, upsert=True)


def restore_from_dump(dev_mongo_uri: str) -> None:
    # Clean up in case of failure
    run_in_docker("rm", "-fr", DUMP_DIR)

    # Dump relevant collections from dev into the mongo container.
    for db, collection in to_copy:
        run_in_docker(
            "mongodump",
            "--uri",
            dev_mongo_uri,
            "--db",
            db,
            "--collection",
            collection,
            "--out",
            DUMP_DIR,
            "--gzip",
        )

    # Restore from dump.
    run_in_docker(
        "mongorestore",
        "--drop",
        "--gzip",
        DUMP_DIR,
    )

    # Clean up the docker container dump path.
    run_in_docker("rm", "-fr", DUMP_DIR)


def run_in_docker(*args: str) -> None:
    subprocess.run(
        ["docker", "compose", "exec", "mongo", *args],  # noqa: S603,S607
        check=True,
    )


if __name__ == "__main__":
    main()
