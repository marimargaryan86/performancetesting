import datetime

import pytest_httpx

from snowfall.vendor.flight_stats import client


async def test_get_flight_status(
    httpx_mock: pytest_httpx.HTTPXMock,
    flight_stats_client: client.FlightStatsClient,
) -> None:
    httpx_mock.add_response(
        url="https://test_url/AA/100/dep/2023/12/21?appId=app_id&appKey=app_key",
        status_code=200,
        json={
            "flight_statuses": [
                {
                    "status": "L",
                    "flight_number": "100",
                    "carrier_fs_code": "AA",
                    "flight_id": 1228889328,
                    "operational_times": {
                        "scheduled_gate_departure": {
                            "date_utc": "2023-12-16T23:55:00.000Z",
                            "date_local": "2023-12-16T18:55:00.000",
                        },
                        "estimated_gate_departure": {
                            "date_utc": "2023-12-17T00:02:00.000Z",
                            "date_local": "2023-12-16T19:02:00.000",
                        },
                    },
                    "airport_resources": {
                        "departure_terminal": "8",
                        "departure_gate": "12",
                        "arrival_terminal": "3",
                        "arrival_gate": "31",
                        "baggage": "10",
                    },
                    "delays": {
                        "arrival_gate_delay_minutes": 7,
                        "departure_gate_delay_minutes": 10,
                    },
                },
            ],
        },
    )

    response = await flight_stats_client.get_flight_status(
        departure_at=datetime.date(2023, 12, 21),
        carrier_code="AA",
        flight_number="100",
    )

    assert response.flight_statuses[0].status == "L"
