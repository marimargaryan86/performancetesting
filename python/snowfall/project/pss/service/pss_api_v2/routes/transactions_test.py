import datetime

from fastapi import status
from fastapi.testclient import TestClient

from snowfall.project.pss.service.pss_api_v2.schemas.transactions import PassengerType


async def test_that_transactions_returns_error_response_when_invalid_app(
    client: TestClient,
) -> None:
    payload = {
        "directions": ["outbound"],
        "channel": "mobile-app",
        "outbound": {
            "destination_id": 0,
            "origin_id": 1,
        },
    }
    resp = client.post(
        "/transactions",
        json=payload,
    )
    assert resp.status_code == status.HTTP_400_BAD_REQUEST
    assert resp.json()["message"] == "Requests for this client are not allowed."


async def test_that_transactions_returns_error_response_when_duplicate_sets(
    client: TestClient,
) -> None:
    payload = {
        "directions": ["outbound"],
        "channel": "desktop",
        "outbound": {
            "destination_id": 0,
            "origin_id": 1,
            "passengers": [
                {"passenger_type_id": PassengerType.adult, "seat_id": 0},
                {"passenger_type_id": PassengerType.adult, "seat_id": 0},
            ],
        },
    }
    resp = client.post("/transactions", json=payload)
    assert resp.status_code == status.HTTP_400_BAD_REQUEST
    assert (
        resp.json()["message"]
        == "Passengers with the same seat_id in a direction are not allowed."
    )


async def test_that_transactions_returns_error_response_when_invalid_transaction(
    client: TestClient,
) -> None:
    payload = {
        "directions": ["outbound"],
        "channel": "desktop",
        "amount": 0,
        "net": 0,
        "vat": 0,
        "locale": "en",
        "transaction_status_id": 0,
        "customer_id": 0,
        "account_id": 0,
        "booking_id": 0,
        "agreement_id": 0,
        "outbound": {
            "date": datetime.date.today().strftime("%Y-%m-%d"),
            "destination_id": 0,
            "origin_id": 0,
            "schedule_id": 0,
            "product_id": 0,
            "passengers": [{"seat_id": 0, "passenger_type_id": 1, "seat_type_id": 0}],
        },
        "inbound": {
            "date": datetime.date.today().strftime("%Y-%m-%d"),
            "destination_id": 0,
            "origin_id": 0,
            "schedule_id": 0,
            "product_id": 0,
            "passengers": [{"seat_id": 0, "passenger_type_id": 1, "seat_type_id": 0}],
        },
    }
    resp = client.post("/transactions", json=payload)
    assert resp.status_code == status.HTTP_400_BAD_REQUEST
    assert (
        resp.json()["message"]
        == "The provided transaction was invalid, see `data` for reasons."
    )
    expected_number_of_reasons = 13
    assert len(resp.json()["data"]) == expected_number_of_reasons
