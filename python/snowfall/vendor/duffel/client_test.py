import datetime

import pytest
import pytest_httpx

from snowfall.vendor.duffel import client, conftest, errors
from snowfall.vendor.duffel.builders.offer_request import (
    OfferRequestPassenger,
    OfferRequestSlice,
    OffersRequestBuilder,
)
from snowfall.vendor.duffel.builders.order_request import (
    IdentityDocument,
    OrderBuilder,
    OrderPassenger,
    OrderPayment,
)

_BASE_URL = "{base_path}{path}"


async def test_offer_request(
    duffel_client: client.DuffelClient,
    httpx_mock: pytest_httpx.HTTPXMock,
) -> None:
    offer_request_create = OffersRequestBuilder()
    offer_request_create.add_passenger(OfferRequestPassenger(pax_type="adult"))
    offer_request_create.add_slice(
        OfferRequestSlice(
            destination="JFK",
            origin="LHR",
            departure_date=datetime.date.today() + datetime.timedelta(days=10),
        ),
    )
    json_res = conftest.load_file_fixture("offer_request_response.json")

    httpx_mock.add_response(
        url=_BASE_URL.format(
            base_path=conftest.API_BASE_URL,
            path="/air/offer_requests",
        ),
        method="POST",
        json=json_res,
    )

    response = await duffel_client.create_offer_request(offer_request_create.build())

    assert response.identifier


async def test_single_offer(
    duffel_client: client.DuffelClient,
    httpx_mock: pytest_httpx.HTTPXMock,
) -> None:
    offer_id = "off_0000AQRKj9nf2S3luPitBA"
    json_res = conftest.load_file_fixture("single_offer.json")

    httpx_mock.add_response(
        url=_BASE_URL.format(
            base_path=conftest.API_BASE_URL,
            path="/air/offers/{id}".format(id=offer_id),
        ),
        method="GET",
        json=json_res,
    )

    response = await duffel_client.get_single_offer(offer_id)

    assert response.identifier


async def test_error(
    duffel_client: client.DuffelClient,
    httpx_mock: pytest_httpx.HTTPXMock,
) -> None:
    offer_id = "off_0000AQRKj9nf2S3luPitBA"
    json_res = conftest.load_file_fixture("errors.json")
    expected_title = (
        "422: Can't book multiple offers from the same offer request, Field"
        " 'selected_offers' has offers included in a offer request"  # noqa: WPS326
        " that has already been booked; please perform a new search"  # noqa: WPS326
    )

    httpx_mock.add_response(
        url=_BASE_URL.format(
            base_path=conftest.API_BASE_URL,
            path="/air/offers/{id}".format(id=offer_id),
        ),
        status_code=422,
        method="GET",
        json=json_res,
    )

    with pytest.raises(errors.ServiceError) as excinfo:
        await duffel_client.get_single_offer(offer_id)

    assert str(excinfo.value) == expected_title  # noqa: WPS441


async def test_error_with_source_str(
    duffel_client: client.DuffelClient,
    httpx_mock: pytest_httpx.HTTPXMock,
) -> None:
    offer_id = "off_0000AQRKj9nf2S3luPitBA"
    json_res = conftest.load_file_fixture("order_create_error.json")
    expected_title = (
        "500: Internal Airline Error, The airline responded"
        " with an internal_error error. Please contact us."  # noqa: WPS326
    )

    httpx_mock.add_response(
        url=_BASE_URL.format(
            base_path=conftest.API_BASE_URL,
            path="/air/offers/{id}".format(id=offer_id),
        ),
        status_code=500,
        method="GET",
        json=json_res,
    )

    with pytest.raises(errors.ServiceError) as excinfo:
        await duffel_client.get_single_offer(offer_id)

    assert str(excinfo.value) == expected_title  # noqa: WPS441


async def test_order_create(
    duffel_client: client.DuffelClient,
    httpx_mock: pytest_httpx.HTTPXMock,
) -> None:
    order_request = OrderBuilder()
    order_request.add_offer_id("off_0000AQDONoycIXZYFfh6N6")
    order_request.add_passenger(
        OrderPassenger(
            title="mr",
            phone_number="+442080160508",
            passenger_id="pas_0000AQDONgVFnpKbyHtXUY",
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
        OrderPayment(payment_type="balance", currency="GBP", amount="1272.76"),
    )
    json_res = conftest.load_file_fixture("order.json")

    httpx_mock.add_response(
        url=_BASE_URL.format(
            base_path=conftest.API_BASE_URL,
            path="/air/orders",
        ),
        method="POST",
        json=json_res,
    )

    response = await duffel_client.order_request(order_request.build())

    assert response.identifier
