import datetime

import pytest
import pytest_httpx

from snowfall.vendor.duffel import client, conftest
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


@pytest.mark.asyncio
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

    assert response


@pytest.mark.asyncio
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

    assert response
