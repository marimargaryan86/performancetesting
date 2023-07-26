import pytest_httpx

from snowfall.vendor.distribusion import client, conftest
from snowfall.vendor.distribusion.models import criterias

_BASE_URL = "{base_path}/retailers/v4/{path}"


async def test_marketing_carriers(
    distribusion_client: client.DistribusionClient,
    httpx_mock: pytest_httpx.HTTPXMock,
) -> None:
    json_res = conftest.load_file_fixture("marketing_carriers_response.json")

    httpx_mock.add_response(
        url=_BASE_URL.format(
            base_path=conftest.API_BASE_URL,
            path="marketing_carriers",
        ),
        method="GET",
        json=json_res,
    )

    response = await distribusion_client.get_marketing_carriers()

    assert response
    assert len(response) == 4
    assert response[1].trade_name == "RegioJet"
    assert response[3].identifier == "VICA"


async def test_marketing_carrier_details(
    distribusion_client: client.DistribusionClient,
    httpx_mock: pytest_httpx.HTTPXMock,
) -> None:
    json_res = conftest.load_file_fixture("marketing_carrier_details_response.json")

    httpx_mock.add_response(
        url=_BASE_URL.format(
            base_path=conftest.API_BASE_URL,
            path="marketing_carriers/VICA?locale=en&currency=EUR",
        ),
        method="GET",
        json=json_res,
    )

    response = await distribusion_client.get_marketing_carrier_details("VICA")

    assert response.address == "Wattstrasse 10"
    assert response.terms == "t&c"
    assert response.authorised_representative == "John Smith"


async def test_get_stations(
    distribusion_client: client.DistribusionClient,
    httpx_mock: pytest_httpx.HTTPXMock,
) -> None:
    json_res = conftest.load_file_fixture("get_stations_response.json")

    httpx_mock.add_response(
        url=_BASE_URL.format(
            base_path=conftest.API_BASE_URL,
            path="stations?locale=en",
        ),
        method="GET",
        json=json_res,
    )

    response = await distribusion_client.get_stations()

    assert response
    assert len(response) == 1
    assert response[0].identifier == "DEFAMFHH"
    assert response[0].zip_code == "60329"


async def test_create_order(
    distribusion_client: client.DistribusionClient,
    httpx_mock: pytest_httpx.HTTPXMock,
) -> None:
    json_req = conftest.load_file_fixture("create_order_request.json")
    json_res = conftest.load_file_fixture("create_order_response.json")

    httpx_mock.add_response(
        url=_BASE_URL.format(
            base_path=conftest.API_BASE_URL,
            path="orders/create",
        ),
        method="POST",
        json=json_res,
    )

    response = await distribusion_client.create_order(criterias.CreateOrder(**json_req))

    assert response.identifier == "VICA-37de14da-6169-4afd-9d68-e90be76b51a1"
    assert response.state == "created"


async def test_get_order(  # noqa: WPS218
    distribusion_client: client.DistribusionClient,
    httpx_mock: pytest_httpx.HTTPXMock,
) -> None:
    order_id = "VICA-37de14da-6169-4afd-9d68-e90be76b51a1"
    json_res = conftest.load_file_fixture("get_order_response.json")

    httpx_mock.add_response(
        url=_BASE_URL.format(
            base_path=conftest.API_BASE_URL,
            path="orders/{order_id}".format(order_id=order_id),
        ),
        method="GET",
        json=json_res,
    )

    response, raw_data = await distribusion_client.get_order(order_id)

    assert response.identifier == order_id
    assert response.currency == "GBP"
    assert response.booking
    assert response.booking.total_price == 2148
    assert response.booking.fare_class
    assert response.booking.fare_class.fare_features
    fare_features = response.booking.fare_class.fare_features
    assert fare_features[10].name == "Accessible area for wheelchairs"
    assert response.booking.passengers
    assert response.booking.passengers[0].first_name == "TEST"
