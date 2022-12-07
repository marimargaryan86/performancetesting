import datetime
import os
import random
import uuid

import pytest

from snowfall.vendor.ba_ndc import client, errors
from snowfall.vendor.ba_ndc.models import (
    payer_details,
    request_name_correction_schemas,
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

    await call_cancel_order(ba_ndc_client, order_rs.identifier)


@disable_by_default
@pytest.mark.asyncio
async def test_get_order(ba_ndc_client: client.BaNdcClient) -> None:
    order_rs = await generate_order(ba_ndc_client)
    assert order_rs is not None
    assert order_rs.order is not None

    order_rs = await ba_ndc_client.get_order(order_rs.identifier)
    assert order_rs is not None
    assert order_rs.order is not None

    await call_cancel_order(ba_ndc_client, order_rs.identifier)


@disable_by_default
@pytest.mark.asyncio
async def test_get_order_with_invalid_order(ba_ndc_client: client.BaNdcClient) -> None:
    invalid_order = "50f5666c-eeee-4b65-8162-d0680f0a7959"
    with pytest.raises(errors.BaNdcError) as error_info:
        await ba_ndc_client.get_order(uuid.UUID(invalid_order))

    assert invalid_order in str(error_info.value)  # noqa: WPS441


@disable_by_default
@pytest.mark.asyncio
async def test_cancel_order(ba_ndc_client: client.BaNdcClient) -> None:
    order_rs = await generate_order(ba_ndc_client)
    assert order_rs is not None
    assert order_rs.order is not None

    await call_cancel_order(ba_ndc_client, order_rs.identifier)


@disable_by_default
@pytest.mark.asyncio
async def test_passenger_name_correction(ba_ndc_client: client.BaNdcClient) -> None:
    order_rs = await generate_order(ba_ndc_client)
    assert order_rs is not None
    assert order_rs.order is not None
    assert order_rs.passengers is not None

    new_passenger_first_name = "Johnnie"
    name_correction = request_name_correction_schemas.NameCorrection(
        current_passenger=request_name_correction_schemas.Passenger(
            passenger_id=order_rs.passengers[0].identifier,
            first_name=order_rs.passengers[0].first_name,
            last_name=order_rs.passengers[0].last_name,
            name_title=order_rs.passengers[0].name_title,
        ),
        new_passenger=request_name_correction_schemas.Passenger(
            passenger_id=order_rs.passengers[0].identifier,
            first_name=new_passenger_first_name,
            last_name=order_rs.passengers[0].last_name,
            name_title=order_rs.passengers[0].name_title,
        ),
    )

    order_rs = await ba_ndc_client.passenger_name_correction(
        order_rs.identifier,
        name_correction,
    )
    assert order_rs is not None and order_rs.order is not None
    assert order_rs.passengers[0].first_name.lower() == new_passenger_first_name.lower()

    await call_cancel_order(ba_ndc_client, order_rs.identifier)


@disable_by_default
@pytest.mark.asyncio
async def test_get_services_by_offer(ba_ndc_client: client.BaNdcClient) -> None:
    offer_searches_rs = await call_get_offers(ba_ndc_client)
    assert offer_searches_rs is not None
    assert offer_searches_rs.offers

    offer = random.choice(offer_searches_rs.offers)  # nosec
    offer_service_rs = await ba_ndc_client.get_services(offer_id=offer.identifier)
    assert offer_service_rs is not None
    assert offer_service_rs.offers


@disable_by_default
@pytest.mark.asyncio
async def test_get_services_by_order(ba_ndc_client: client.BaNdcClient) -> None:
    order_rs = await generate_order(ba_ndc_client)
    assert order_rs is not None
    assert order_rs.order is not None

    order_service_rs = await ba_ndc_client.get_services(order_id=order_rs.identifier)
    assert order_service_rs is not None
    assert order_service_rs.offers

    await call_cancel_order(ba_ndc_client, order_rs.identifier)


@disable_by_default
@pytest.mark.asyncio
async def test_get_seats_by_offer(ba_ndc_client: client.BaNdcClient) -> None:
    offer_searches_rs = await call_get_offers(ba_ndc_client)
    assert offer_searches_rs is not None
    assert offer_searches_rs.offers

    offer = random.choice(offer_searches_rs.offers)  # nosec
    offer_search_rs = await ba_ndc_client.get_offer(offer.identifier)
    seats_rs = await ba_ndc_client.get_seats(offer_id=offer_search_rs.offer.identifier)
    assert seats_rs is not None
    assert seats_rs.seat_maps


@disable_by_default
@pytest.mark.asyncio
async def test_get_seats_by_order(ba_ndc_client: client.BaNdcClient) -> None:
    order_rs = await generate_order(ba_ndc_client)
    assert order_rs is not None
    assert order_rs.order is not None

    seats_rs = await ba_ndc_client.get_seats(order_id=order_rs.identifier)
    assert seats_rs is not None
    assert seats_rs.seat_maps

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
