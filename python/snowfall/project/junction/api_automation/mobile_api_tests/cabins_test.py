import json
import logging

import pytest

from snowfall.project.junction.api_automation.test_functions.mobile_client import (
    MobileApiClient,
)

logging.basicConfig()
logging.getLogger().setLevel(logging.INFO)


@pytest.mark.integration()
async def test_cabin_classes_ids_mobile(
    mobile_client: MobileApiClient,
) -> None:
    expected_classes = {"business", "economy", "first", "premium", "unspecified"}
    r0 = await mobile_client.list_cabin_classes()
    logging.info("list_cabin_classes: %s", json.dumps(r0, indent=4))
    cabin_classes_ids = []
    for idx, _ in enumerate(r0["data"]):
        cabin_classes_ids.append(r0["data"][idx]["id"])
    logging.info("cabin_classes: %s", cabin_classes_ids)
    assert set(cabin_classes_ids) == expected_classes  # nosec
