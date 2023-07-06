import json
import logging

import pytest

from snowfall.project.junction.api_automation.test_functions.mobile_client import (
    MobileApiClient,
)

logging.basicConfig()
logging.getLogger().setLevel(logging.INFO)


@pytest.mark.skip(reason="temporary skipped")
async def test_cabin_classes_ids_mobile(
    mobile_client: MobileApiClient,
) -> None:
    expected_classes = {"business", "economy", "first", "premium", "unspecified"}
    r0 = await mobile_client.list_cabin_classes()
    logging.info("list_cabin_classes: %s", json.dumps(r0, indent=4))
    cabin_classes_ids = [cabin_class["id"] for cabin_class in r0["data"]]
    logging.info("cabin_classes: %s", cabin_classes_ids)
    assert set(cabin_classes_ids) == expected_classes
