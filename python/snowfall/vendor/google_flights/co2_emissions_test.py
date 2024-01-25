import pytest_httpx

from snowfall.vendor.google_flights import co2_emissions
from snowfall.vendor.google_flights.models import emissions as co2_emissions_models


async def test_get_emissions(
    httpx_mock: pytest_httpx.HTTPXMock,
    co2_emissions_client: co2_emissions.Client,
) -> None:
    httpx_mock.add_response(
        url="https://test_url/?key=key",
        method="POST",
        status_code=200,
        json={
            "flight_emissions": [
                {
                    "flight": {
                        "origin": "ZRH",
                        "destination": "CDG",
                        "operating_carrier_code": "AF",
                        "flight_number": 1115,
                        "departure_date": {
                            "year": 2024,
                            "month": 6,
                            "day": 1,
                        },
                    },
                    "emissions_grams_per_pax": {
                        "first": 7400,
                        "business": 7400,
                        "premium_economy": 4900,
                        "economy": 4900,
                    },
                },
            ],
        },
    )

    response = await co2_emissions_client.get_emissions(
        flights=(
            co2_emissions_models.Flight(
                origin="ZRH",
                destination="CDG",
                operating_carrier_code="AF",
                flight_number=1115,
                departure_date={
                    "year": 2024,
                    "month": 6,
                    "day": 1,
                },
            ),
        ),
    )

    assert len(response.flight_emissions) == 1
