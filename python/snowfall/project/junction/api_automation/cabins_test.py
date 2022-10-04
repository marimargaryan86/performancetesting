import json
import logging

import httpx
import pytest

from snowfall.vendor.junction.client import JunctionClient

logging.basicConfig()
logging.getLogger().setLevel(logging.INFO)


@pytest.mark.integration
async def test_list_cabin_classes(
    host: str,
    api_token: str,
) -> None:
    client = JunctionClient(
        api_url="https://{0}".format(host),
        token=api_token,
        client=httpx.AsyncClient(timeout=10),
    )

    response = await client.list_cabin_classes()
    logging.info("list_cabin_classes: %s", json.dumps(response, indent=4))
    assert response["data"][0]["id"] == "unspecified"
    assert response["data"][1]["id"] == "economy"
    assert response["data"][2]["id"] == "premium"
    assert response["data"][3]["id"] == "business"
    assert response["data"][4]["id"] == "first"


@pytest.mark.integration
async def test_get_cabin_class(
    host: str,
    api_token: str,
) -> None:
    client = JunctionClient(api_url="https://{0}".format(host), token=api_token)

    cabin_classes_ids = await return_cabin_classes_ids(client)

    for cabin_class_id in cabin_classes_ids:
        r1 = await client.get_cabin_class(cabin_class_id)
        logging.info("get_cabin_class: %s", json.dumps(r1, indent=4))
        assert r1["data"]["attributes"]["name"] == cabin_class_id


async def return_cabin_classes_ids(
    client: JunctionClient,
) -> list[str]:
    r0 = await client.list_cabin_classes()
    logging.info("list_cabin_classes: %s", json.dumps(r0, indent=4))
    cabin_classes_ids = []
    for idx, _ in enumerate(r0["data"]):
        cabin_classes_ids.append(r0["data"][idx]["id"])
    logging.info("cabin_classes: %s", cabin_classes_ids)
    return cabin_classes_ids
