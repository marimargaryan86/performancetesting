import pytest_httpx

from snowfall.vendor.distribusion import client, conftest

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

    assert response
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
    assert response[0] and response[0].identifier == "DEFAMFHH"
    assert response[0] and response[0].zip_code == "60329"
