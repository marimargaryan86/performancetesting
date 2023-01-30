import datetime
import os

import pytest

from snowfall.vendor.duffel import client
from snowfall.vendor.duffel.builders.offer_request import (
    OfferRequestPassenger,
    OfferRequestSlice,
    OffersRequestBuilder,
)
from snowfall.vendor.duffel.builders.order_cancel import OrderCancelRequestBuilder
from snowfall.vendor.duffel.builders.order_request import (
    IdentityDocument,
    OrderBuilder,
    OrderPassenger,
    OrderPayment,
)

disable_by_default = pytest.mark.skipif(
    os.getenv("DUFFEL_TESTS") != "ENABLED",
    reason="To enable set env variable DUFFEL_TESTS=ENABLED",
)


@disable_by_default
async def test_request_offers(duffel_client: client.DuffelClient) -> None:
    offer_request_create = OffersRequestBuilder()
    offer_request_create.add_passenger(OfferRequestPassenger(pax_type="adult"))
    offer_request_create.add_slice(
        OfferRequestSlice(
            origin="LHR",
            destination="SYD",
            departure_date=datetime.date.fromisoformat("2023-02-26"),
        ),
    )

    offers = await duffel_client.create_offer_request(offer_request_create.build())
    assert offers is not None


@disable_by_default
async def test_request_round_trip_offers(duffel_client: client.DuffelClient) -> None:
    offer_request_create = OffersRequestBuilder()
    offer_request_create.add_passenger(OfferRequestPassenger(pax_type="adult"))
    offer_request_create.add_slice(
        OfferRequestSlice(
            destination="JFK",
            origin="LHR",
            departure_date=datetime.date.today() + datetime.timedelta(days=10),
        ),
    )
    offer_request_create.add_slice(
        OfferRequestSlice(
            destination="LHR",
            origin="JFK",
            departure_date=datetime.date.today() + datetime.timedelta(days=15),
        ),
    )

    offers = await duffel_client.create_offer_request(offer_request_create.build())
    assert offers is not None


@disable_by_default
async def test_get_offers(duffel_client: client.DuffelClient) -> None:
    offer_id = "off_0000AQRKj9nf2S3luPitBA"
    offers = await duffel_client.get_single_offer(offer_id)
    assert offers is not None


@disable_by_default
async def test_seat_map(duffel_client: client.DuffelClient) -> None:
    offer_id = "off_0000ASApQL0LdDq30usAoj"
    seats = await duffel_client.get_seat_map(offer_id)
    assert seats is not None


@disable_by_default
async def test_order_create(duffel_client: client.DuffelClient) -> None:
    offer_request_create = OffersRequestBuilder()
    offer_request_create.add_passenger(OfferRequestPassenger(pax_type="adult"))
    offer_request_create.add_slice(
        OfferRequestSlice(
            destination="JFK",
            origin="LHR",
            departure_date=datetime.date.today() + datetime.timedelta(days=14),
        ),
    )
    offers = await duffel_client.create_offer_request(offer_request_create.build())
    offer = offers.offers[0]

    order_request = OrderBuilder()
    order_request.add_offer_id(offer.identifier)
    order_request.add_passenger(
        OrderPassenger(
            title="mr",
            phone_number="+442080160508",
            passenger_id=offer.passengers[0].identifier,
            given_name="SNOWFALL",
            gender="m",
            family_name="TRAVEL",
            email="conelia.corde@duffel.com",
            born_on=datetime.date.today() - datetime.timedelta(weeks=1300),
            identity_documents=[
                IdentityDocument(
                    unique_identifier="19KL56147",
                    document_type="passport",
                    issuing_country_code="GB",
                    expires_on=datetime.date.today() + datetime.timedelta(weeks=210),
                ),
            ],
        ),
    )
    order_request.add_payment(
        OrderPayment(
            payment_type="balance",
            currency=offer.total_currency,
            amount=offer.total_amount,
        ),
    )

    order = await duffel_client.order_request(order_request.build())
    assert order is not None


@disable_by_default
async def test_get_order(duffel_client: client.DuffelClient) -> None:
    order_response = await duffel_client.get_order("ord_0000AQLMc7fLefajMkhgDh")
    assert order_response is not None


@disable_by_default
async def test_order_cancel(duffel_client: client.DuffelClient) -> None:
    order_cancel_request = OrderCancelRequestBuilder()
    order_cancel_request.order_type("ord_0000AQLMc7fLefajMkhgDh")

    order_cancel_response = await duffel_client.cancel_order_request(
        order_cancel_request.build(),
    )

    order_cancel_response = await duffel_client.cancel_order_confirm(
        order_cancel_response.identifier,
    )
    assert order_cancel_response is not None
