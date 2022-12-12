import json
import logging

import pytest

from snowfall.vendor.junction.client import JunctionClient

logging.basicConfig()
logging.getLogger().setLevel(logging.INFO)


@pytest.mark.integration
async def test_list_cabin_classes(
    junction_client: JunctionClient,
) -> None:
    response = await junction_client.list_cabin_classes()
    logging.info("list_cabin_classes: %s", json.dumps(response, indent=4))
    classes = {cabin["id"] for cabin in response["data"]}
    assert classes == {"unspecified", "economy", "premium", "business", "first"}


@pytest.mark.integration
async def test_get_cabin_class(
    junction_client: JunctionClient,
) -> None:
    cabin_classes_ids = await return_cabin_classes_ids(junction_client)

    for cabin_class_id in cabin_classes_ids:
        r1 = await junction_client.get_cabin_class(cabin_class_id)
        logging.info("get_cabin_class: %s", json.dumps(r1, indent=4))
        assert r1["data"]["attributes"]["name"] == cabin_class_id


async def return_cabin_classes_ids(
    junction_client: JunctionClient,
) -> list[str]:
    r0 = await junction_client.list_cabin_classes()
    logging.info("list_cabin_classes: %s", json.dumps(r0, indent=4))
    cabin_classes_ids = []
    for idx, _ in enumerate(r0["data"]):
        cabin_classes_ids.append(r0["data"][idx]["id"])
    logging.info("cabin_classes: %s", cabin_classes_ids)
    return cabin_classes_ids
