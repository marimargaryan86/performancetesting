import datetime
import os
import random
import uuid

import pytest

from snowfall.vendor.ba_ndc import client
from snowfall.vendor.ba_ndc.models import (
    payer_details,
    request_offer_search_schemas,
    request_order_schemas,
    response_offer_search_schemas,
    response_order_schemas,
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


@disable_by_default
@pytest.mark.asyncio
async def test_get_offer(ba_ndc_client: client.BaNdcClient) -> None:
    offer_searches_rs = await call_get_offers(ba_ndc_client)
    offer = random.choice(offer_searches_rs.offers)  # nosec
    offer_search_rs = await ba_ndc_client.get_offer(offer.identifier)

    assert offer_search_rs is not None
    assert offer_search_rs.offer is not None


@disable_by_default
@pytest.mark.asyncio
async def test_create_order(ba_ndc_client: client.BaNdcClient) -> None:
    order_rs = await generate_order(ba_ndc_client)
    assert order_rs is not None
    assert order_rs.order is not None


@disable_by_default
@pytest.mark.asyncio
async def test_cancel_order(ba_ndc_client: client.BaNdcClient) -> None:
    order_rs = await generate_order(ba_ndc_client)
    assert order_rs is not None
    assert order_rs.order is not None

    await call_cancel_order(ba_ndc_client, order_rs.identifier)


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


async def generate_order(
    ba_ndc_client: client.BaNdcClient,
) -> response_order_schemas.OrderResponse:
    offer_searches_rs = await call_get_offers(ba_ndc_client)
    offer = random.choice(offer_searches_rs.offers)  # nosec
    offer_search_rs = await ba_ndc_client.get_offer(offer.identifier)

    assert offer_search_rs is not None
    assert offer_search_rs.offer is not None

    return await call_create_order(ba_ndc_client, offer_search_rs.offer.identifier)


async def call_create_order(
    ba_ndc_client: client.BaNdcClient,
    offer_id: uuid.UUID,
) -> response_order_schemas.OrderResponse:
    order_rq = request_order_schemas.CreateOrderRequest(
        offer_id=offer_id,
        passengers=[
            request_order_schemas.PassengerExtended(
                identifier="PA0",
                passenger_type=util.passenger_enums.PassengerTypeEnum.adult,
                first_name="John",
                last_name="Doe",
                name_title="MR",
                birth_date=datetime.date.fromisoformat("1970-01-01"),
                gender=util.passenger_enums.GenderEnum.male,
                contact=request_order_schemas.Contact(
                    email="john.doe@snowfall.com",
                    phone=payer_details.Phone(
                        phone_type=util.passenger_enums.PhoneTypeEnum.mobile,
                        number="15141234567",
                    ),
                ),
            ),
        ],
        payment=None,
    )

    return await ba_ndc_client.create_order(order_rq)


async def call_cancel_order(
    ba_ndc_client: client.BaNdcClient,
    order_id: uuid.UUID,
) -> None:
    await ba_ndc_client.cancel_order(order_id)
