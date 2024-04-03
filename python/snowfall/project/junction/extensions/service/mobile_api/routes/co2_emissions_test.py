from collections.abc import Mapping

import httpx
from starlette import status

_CO2EMISSION_URL = "/co2-emissions"


class TestCo2Emission:
    async def test_co2emission_post(
        self,
        authenticated_http_client: httpx.AsyncClient,
        headers: Mapping[str, str],
    ) -> None:
        response = await authenticated_http_client.post(
            _CO2EMISSION_URL,
            json={
                "data": {
                    "attributes": {
                        "flights": [
                            {
                                "origin": "LHR",
                                "destination": "ATH",
                                "operatingCarrierCode": "AA",
                                "flightNumber": 100,
                                "departureDate": "2019-08-24",
                            },
                        ],
                    },
                },
            },
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["data"][0]["id"] == "AA100"
