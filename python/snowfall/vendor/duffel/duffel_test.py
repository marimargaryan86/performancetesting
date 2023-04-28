import datetime
import hashlib
import json
import os
from time import sleep

import pytest

from snowfall.vendor.duffel import client
from snowfall.vendor.duffel.builders.offer_request import (
    OfferRequestPassenger,
    OfferRequestSlice,
    OfferRequestSliceTimeRange,
    OffersRequestBuilder,
)
from snowfall.vendor.duffel.builders.order_cancel import OrderCancelRequestBuilder
from snowfall.vendor.duffel.builders.order_request import (
    IdentityDocument,
    OrderBuilder,
    OrderPassenger,
    OrderPayment,
)
from snowfall.vendor.duffel.models.offer import Offer

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
async def test_request_offers_with_infant(duffel_client: client.DuffelClient) -> None:
    offer_request_create = OffersRequestBuilder()
    offer_request_create.add_passenger(OfferRequestPassenger(age=30))
    offer_request_create.add_passenger(OfferRequestPassenger(age=1))
    offer_request_create.add_slice(
        OfferRequestSlice(
            origin="LHR",
            destination="SYD",
            departure_date=datetime.date.fromisoformat("2023-05-26"),
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
    offer_id = "off_0000AV4x20zCNTVvjwE0zE"
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
async def test_offer_after_order_create(  # noqa: WPS210
    duffel_client: client.DuffelClient,
) -> None:
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

    if offer.passenger_identity_documents_required:
        identity_documents = [
            IdentityDocument(
                unique_identifier="19KL56147",
                document_type="passport",
                issuing_country_code="GB",
                expires_on=datetime.date.today() + datetime.timedelta(weeks=210),
            ),
        ]
    else:
        identity_documents = None

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
            identity_documents=identity_documents,
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
    sleep(10)

    # get offer after order creation
    single_offer = await duffel_client.get_single_offer(offer.identifier)
    assert single_offer is not None

    # second offer
    offer = await refresh_offer(duffel_client, offers.offers[1])

    if offer.passenger_identity_documents_required:
        identity_documents = [
            IdentityDocument(
                unique_identifier="19KL56147",
                document_type="passport",
                issuing_country_code="GB",
                expires_on=datetime.date.today() + datetime.timedelta(weeks=210),
            ),
        ]
    else:
        identity_documents = None

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
            identity_documents=identity_documents,
        ),
    )
    order_request.add_payment(
        OrderPayment(
            payment_type="balance",
            currency=offer.total_currency,
            amount=offer.total_amount,
        ),
    )

    order2 = await duffel_client.order_request(order_request.build())
    assert order2 is not None


@disable_by_default
async def test_brussels_airline_refresh_offer(
    duffel_client: client.DuffelClient,
) -> None:
    offer = await duffel_client.get_single_offer("off_0000AV6qLwWut9cBOA4b0y")
    refreshed_offer = await refresh_offer(duffel_client, offer)
    assert refreshed_offer is not None


async def refresh_offer(  # noqa: WPS210
    duffel_client: client.DuffelClient,
    offer: Offer,
) -> Offer:
    offer_request_create = OffersRequestBuilder()

    for passenger in offer.passengers:
        offer_request_create.add_passenger(
            OfferRequestPassenger(pax_type=passenger.passenger_type, age=passenger.age),
        )

    for offer_slice in offer.slices:
        first_segment = offer_slice.segments[0]
        last_segment = offer_slice.segments[-1]
        offer_request_create.add_slice(
            OfferRequestSlice(
                destination=last_segment.destination.iata_code or "",
                origin=first_segment.origin.iata_code or "",
                departure_date=first_segment.departing_at.date(),
                departure_time=OfferRequestSliceTimeRange(
                    time_from=first_segment.departing_at.strftime("%H:%M"),
                    to=(
                        first_segment.departing_at + datetime.timedelta(minutes=1)
                    ).strftime("%H:%M"),
                ),
                arrival_time=OfferRequestSliceTimeRange(
                    time_from=last_segment.arriving_at.strftime("%H:%M"),
                    to=(
                        last_segment.arriving_at + datetime.timedelta(minutes=1)
                    ).strftime("%H:%M"),
                ),
            ),
        )

    offers = await duffel_client.create_offer_request(offer_request_create.build())
    offer_hash = get_offer_hash(offer)
    renewed_offer: Offer | None = None

    for new_offer in offers.offers:
        if get_offer_hash(new_offer) == offer_hash:
            renewed_offer = new_offer
            break

    assert renewed_offer is not None
    return renewed_offer


def get_offer_hash(offer: Offer) -> str:
    reduced_offer = {
        "slices": [
            {
                "segments": [
                    {
                        "passengers": [
                            {
                                "fare_basis_code": passenger.fare_basis_code,
                                "cabin_class_marketing_name": (
                                    passenger.cabin_class_marketing_name
                                ),
                                "cabin_class": passenger.cabin_class,
                            }
                            for passenger in segment.passengers
                        ],
                        "origin": segment.origin.iata_code,
                        "destination": segment.destination.iata_code,
                        "operating_flight_number": (
                            segment.operating_carrier_flight_number
                        ),
                        "operating_carrier_code": segment.operating_carrier.iata_code,
                        "marketing_carrier_code": segment.marketing_carrier.iata_code,
                        "marketing_flight_number": (
                            segment.marketing_carrier_flight_number
                        ),
                        "departing_at": segment.departing_at,
                        "arriving_at": segment.arriving_at,
                    }
                    for segment in offer_slice.segments
                ],
                "fare_brand_name": offer_slice.fare_brand_name,
            }
            for offer_slice in offer.slices
        ],
    }

    return hashlib.md5(
        json.dumps(reduced_offer, sort_keys=True, default=str).encode(),
        usedforsecurity=False,
    ).hexdigest()


@disable_by_default
async def test_order_create_with_infant(duffel_client: client.DuffelClient) -> None:
    offer_request_create = OffersRequestBuilder()
    offer_request_create.add_passenger(OfferRequestPassenger(pax_type="adult"))
    offer_request_create.add_passenger(OfferRequestPassenger(age=1))
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
            infant_passenger_id=offer.passengers[1].identifier,
            given_name="SNOWFALL",
            gender="m",
            family_name="TRAVEL",
            email="conelia.corde@duffel.com",
            born_on=datetime.date.today() - datetime.timedelta(weeks=1300),
        ),
    )
    order_request.add_passenger(
        OrderPassenger(
            title="mr",
            phone_number="+442080160508",
            passenger_id=offer.passengers[1].identifier,
            given_name="SNOWFALLKid",
            gender="m",
            family_name="TRAVEL",
            email="conelia.corde@duffel.com",
            born_on=datetime.date.today() - datetime.timedelta(weeks=52),
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
