import datetime
import os
import random
import uuid

import pytest

from snowfall.vendor.ba_ndc import client, errors
from snowfall.vendor.ba_ndc.adapters.offers_response_adapter import (
    OffersResponseAdapter,
)
from snowfall.vendor.ba_ndc.builders import offer_request, order_request
from snowfall.vendor.ba_ndc.models import (
    request_add_seat_schemas,
    request_name_correction_schemas,
    request_offer_search_schemas,
    request_order_change_schemas,
    request_order_schemas,
    response_common_passenger_schemas,
    response_order_schemas,
)
from snowfall.vendor.ba_ndc.models.util import offer_enums, passenger_enums

disable_by_default = pytest.mark.skipif(
    os.getenv("BA_NDC_TESTS") != "ENABLED",
    reason="To enable set env variable BA_NDC_TESTS=ENABLED",
)


@disable_by_default
async def test_get_offers(ba_ndc_client: client.BaNdcClient) -> None:
    offer_searches_rs = await call_get_offers(ba_ndc_client)
    assert offer_searches_rs is not None
    assert offer_searches_rs.get_offers()


@disable_by_default
async def test_get_offer(ba_ndc_client: client.BaNdcClient) -> None:
    offer_searches_rs = await call_get_offers(ba_ndc_client)
    offer = random.choice(offer_searches_rs.get_offers())  # nosec
    offer_search_rs = await ba_ndc_client.get_offer(offer.identifier)

    assert offer_search_rs is not None
    assert offer_search_rs.offer is not None


@disable_by_default
async def test_create_order(ba_ndc_client: client.BaNdcClient) -> None:
    order_rs = await generate_order(ba_ndc_client)
    assert order_rs is not None
    assert order_rs.order is not None

    await call_cancel_order(ba_ndc_client, order_rs.identifier)


@disable_by_default
async def test_get_order(ba_ndc_client: client.BaNdcClient) -> None:
    order_rs = await generate_order(ba_ndc_client)
    assert order_rs is not None
    assert order_rs.order is not None

    order_rs = await ba_ndc_client.get_order(order_rs.identifier)
    assert order_rs is not None
    assert order_rs.order is not None

    await call_cancel_order(ba_ndc_client, order_rs.identifier)


@disable_by_default
async def test_get_order_with_invalid_order(ba_ndc_client: client.BaNdcClient) -> None:
    invalid_order = "50f5666c-eeee-4b65-8162-d0680f0a7959"
    with pytest.raises(errors.BaNdcError) as error_info:
        await ba_ndc_client.get_order(uuid.UUID(invalid_order))

    assert invalid_order in str(error_info.value)  # noqa: WPS441


@disable_by_default
async def test_cancel_order(ba_ndc_client: client.BaNdcClient) -> None:
    order_rs = await generate_order(ba_ndc_client)
    assert order_rs is not None
    assert order_rs.order is not None

    await call_cancel_order(ba_ndc_client, order_rs.identifier)


@disable_by_default
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
    assert order_rs.order is not None
    assert order_rs.passengers[0].first_name.lower() == new_passenger_first_name.lower()

    await call_cancel_order(ba_ndc_client, order_rs.identifier)


@disable_by_default
async def test_update_order(ba_ndc_client: client.BaNdcClient) -> None:
    order_rs = await generate_order(ba_ndc_client)
    assert order_rs is not None
    assert order_rs.order is not None

    passenger = order_rs.passengers[0]
    request = request_order_schemas.UpdateOrderRequest(
        passengers=[
            request_order_schemas.PassengerPartial(
                identifier=passenger.identifier,
                first_name=passenger.first_name,
                last_name=passenger.last_name,
                name_title=passenger.name_title,
                identity_documents=[
                    request_order_schemas.IdentityDocument(
                        document_number="7534567891",
                        document_type="PT",
                        birth_date=passenger.birth_date
                        or datetime.date.fromisoformat("1970-01-01"),
                        nationality="GBR",
                        issuing_country="GBR",
                        expiration_date=datetime.date.fromisoformat("2027-07-08"),
                    ),
                ],
            ),
        ],
        payment=None,
    )

    order_rs = await ba_ndc_client.update_order(order_rs.identifier, request)
    assert order_rs is not None
    assert order_rs.order is not None

    await call_cancel_order(ba_ndc_client, order_rs.identifier)


@disable_by_default
async def test_get_services_by_offer(ba_ndc_client: client.BaNdcClient) -> None:
    offer_searches_rs = await call_get_offers(ba_ndc_client)
    assert offer_searches_rs is not None
    assert offer_searches_rs.get_offers()

    offer = random.choice(offer_searches_rs.get_offers())  # nosec
    offer_service_rs = await ba_ndc_client.get_services(offer_id=offer.identifier)
    assert offer_service_rs is not None
    assert offer_service_rs.offers


@disable_by_default
async def test_get_services_by_order(ba_ndc_client: client.BaNdcClient) -> None:
    order_rs = await generate_order(ba_ndc_client)
    assert order_rs is not None
    assert order_rs.order is not None

    order_service_rs = await ba_ndc_client.get_services(order_id=order_rs.identifier)
    assert order_service_rs is not None
    assert order_service_rs.offers

    await call_cancel_order(ba_ndc_client, order_rs.identifier)


@disable_by_default
async def test_get_seats_by_offer(ba_ndc_client: client.BaNdcClient) -> None:
    offer_searches_rs = await call_get_offers(ba_ndc_client)
    assert offer_searches_rs is not None
    assert offer_searches_rs.get_offers()

    offer = random.choice(offer_searches_rs.get_offers())  # nosec
    offer_search_rs = await ba_ndc_client.get_offer(offer.identifier)
    seats_rs = await ba_ndc_client.get_seats(offer_id=offer_search_rs.offer.identifier)
    assert seats_rs is not None
    assert seats_rs.seat_maps


@disable_by_default
async def test_get_seats_by_order(ba_ndc_client: client.BaNdcClient) -> None:
    order_rs = await generate_order(ba_ndc_client)
    assert order_rs is not None
    assert order_rs.order is not None

    seats_rs = await ba_ndc_client.get_seats(order_id=order_rs.identifier)
    assert seats_rs is not None
    assert seats_rs.seat_maps

    await call_cancel_order(ba_ndc_client, order_rs.identifier)


@disable_by_default
async def test_add_seat(ba_ndc_client: client.BaNdcClient) -> None:
    order_rs = await generate_order(ba_ndc_client)
    assert order_rs is not None
    assert order_rs.order is not None

    seats_rs = await ba_ndc_client.get_seats(order_id=order_rs.identifier)
    assert seats_rs.seat_maps
    seat = random.choice(  # nosec
        random.choice(random.choice(seats_rs.seat_maps).cabins).seats,  # nosec
    )

    request = request_add_seat_schemas.AddSeats(
        pairs=[
            request_add_seat_schemas.SeatPassengerPair(
                seat_id=str(seat.identifier),
                passenger_id=seat.passenger_ids[0],
            ),
        ],
        payment=None,
    )

    order_rs = await ba_ndc_client.add_seat(order_rs.identifier, request)
    seat_item = next(
        seat_elem
        for seat_elem in order_rs.order.order_items
        if isinstance(seat_elem, response_order_schemas.SeatOrderItem)
    )

    assert order_rs is not None
    assert seat_item.column == seat.column

    await call_cancel_order(ba_ndc_client, order_rs.identifier)


@disable_by_default
async def test_reshop(ba_ndc_client: client.BaNdcClient) -> None:
    order_rs = await generate_order(ba_ndc_client)
    assert order_rs is not None
    assert order_rs.origin_destinations

    reshop_rq = request_order_change_schemas.OrderReshopRequest(
        cabin_preference=offer_enums.CabinTypeEnum.first,
        origin_destinations=[
            request_order_change_schemas.OriginDestination(
                identifier=order_rs.origin_destinations[0].identifier,
                departure_date=order_rs.origin_destinations[
                    0
                ].departure_date_time.date()
                + datetime.timedelta(days=1),
            ),
        ],
    )

    reshop_rs = await ba_ndc_client.reshop(order_rs.identifier, reshop_rq)
    assert reshop_rs is not None
    assert reshop_rs.offers

    await call_cancel_order(ba_ndc_client, order_rs.identifier)


async def call_get_offers(
    ba_ndc_client: client.BaNdcClient,
) -> OffersResponseAdapter:
    offers_request_builder = offer_request.OffersRequestBuilder()
    offers_request_builder.add_passenger(passenger_enums.PassengerTypeEnum.adult)
    offers_request_builder.add_trip(
        request_offer_search_schemas.Trip(
            origin="LHR",
            destination="MAN",
            date=datetime.datetime.now(datetime.timezone.utc)
            + datetime.timedelta(
                days=45,
            ),
            time=datetime.time.fromisoformat("08:00"),
        ),
    )

    return await ba_ndc_client.get_offers(offers_request_builder.build())


async def generate_order(
    ba_ndc_client: client.BaNdcClient,
) -> response_order_schemas.OrderResponse:
    offer_searches_rs = await call_get_offers(ba_ndc_client)
    offer = random.choice(offer_searches_rs.get_offers())  # nosec
    offer_search_rs = await ba_ndc_client.get_offer(offer.identifier)

    assert offer_search_rs is not None
    assert offer_search_rs.offer is not None

    order_request_builder = order_request.OrderRequestBuilder(
        offer_search_rs.offer.identifier,
    )
    order_request_builder.add_passenger(
        request_order_schemas.PassengerExtended(
            identifier="PA0",
            passenger_type=passenger_enums.PassengerTypeEnum.adult,
            first_name="John",
            last_name="Doe",
            name_title="MR",
            birth_date=datetime.date.fromisoformat("1970-01-01"),
            gender=passenger_enums.GenderEnum.male,
            contact=request_order_schemas.Contact(
                email="john.doe@snowfall.com",
                phone=response_common_passenger_schemas.Phone(
                    phone_type=passenger_enums.PhoneTypeEnum.mobile,
                    number="15141234567",
                ),
            ),
        ),
    )

    return await ba_ndc_client.create_order(order_request_builder.build())


async def call_cancel_order(
    ba_ndc_client: client.BaNdcClient,
    order_id: uuid.UUID,
) -> None:
    await ba_ndc_client.cancel_order(order_id)
