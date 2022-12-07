import datetime
import os

import pytest

from snowfall.vendor.ba_ndc import client
from snowfall.vendor.ba_ndc.models import (
    request_offer_search_schemas,
    response_offer_search_schemas,
    util,
)

disable_by_default = pytest.mark.skipif(
    os.getenv("BA_NDC_TESTS") != "ENABLED",
    reason="To enable set env variable BA_NDC_TESTS=ENABLED",
)


@disable_by_default
@pytest.mark.asyncio
async def test_get_offers(ba_ndc_client: client.BaNdcClient) -> None:
    offer_searches_rs = await call_get_offers(ba_ndc_client)
    assert offer_searches_rs is not None
    assert offer_searches_rs.offers


async def call_get_offers(
    ba_ndc_client: client.BaNdcClient,
) -> response_offer_search_schemas.OfferSearchResponse:
    offer_search_rq = request_offer_search_schemas.OfferSearchRequest(
        cabin_type=util.offer_enums.CabinTypeEnum.economy,
        fare_preferences={
            util.offer_enums.FareGroupEnum.fare_rules,
        },
        passengers=[
            request_offer_search_schemas.Passenger(
                passenger_type=util.passenger_enums.PassengerTypeEnum.adult,
                birth_date=datetime.date.fromisoformat("1970-01-01"),
            ),
        ],
        trips=[
            request_offer_search_schemas.Trip(
                origin="LHR",
                destination="MAN",
                date=datetime.date.fromisoformat("2023-01-30"),
                time=datetime.time.fromisoformat("08:00"),
            ),
        ],
    )

    return await ba_ndc_client.get_offers(offer_search_rq)
