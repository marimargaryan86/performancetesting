import pytest_httpx

from snowfall.vendor.benerail import client, conftest
from snowfall.vendor.benerail.models.dialogue import passenger

_BOOKING_BASE_PATH = "bookings/bookings"
_DIALOGUE_BASE_PATH = "dialogue-engine/dialogues"
_TRIP_OFFER_PATH = "trip-offers"
_FAKE_ETAG = "random"


async def test_get_booking(
    httpx_mock: pytest_httpx.HTTPXMock,
    benerail_client: client.BenerailClient,
) -> None:
    json_res = conftest.load_file_fixture("get_booking_response.json")

    httpx_mock.add_response(
        url="{base_path}/{booking_path}/{booking_id}".format(
            base_path=conftest.API_BASE_URL,
            booking_path=_BOOKING_BASE_PATH,
            booking_id="00000000-0000-0000-0000-000000000000",
        ),
        method="GET",
        json=json_res,
        headers={"etag": "testetag"},
    )

    booking = await benerail_client.bookings_client.get_booking(
        booking_id="00000000-0000-0000-0000-000000000000",
    )

    if booking.response_result is not None:
        assert (
            booking.response_result.identifier == "00000000-0000-0000-0000-000000000000"
        )


async def test_create_dialogue(
    httpx_mock: pytest_httpx.HTTPXMock,
    benerail_client: client.BenerailClient,
) -> None:
    json_res = conftest.load_file_fixture("get_dialogue.json")

    httpx_mock.add_response(
        url="{base_path}/{dialogue_path}".format(
            base_path=conftest.API_BASE_URL,
            dialogue_path=_DIALOGUE_BASE_PATH,
        ),
        method="POST",
        json=json_res,
        headers={"etag": _FAKE_ETAG},
    )

    dialogue = await benerail_client.dialogue.create_dialogue()

    assert dialogue.response_result.identifier == "00000000-0000-0000-0000-000000000000"


async def test_create_passenger(
    httpx_mock: pytest_httpx.HTTPXMock,
    benerail_client: client.BenerailClient,
) -> None:
    json_req = conftest.load_file_fixture("create_passenger_request.json")
    json_res = conftest.load_file_fixture("create_passenger_response.json")

    httpx_mock.add_response(
        url="{base_path}/{dialogue_path}/{dialogue_id}/passengers".format(
            base_path=conftest.API_BASE_URL,
            dialogue_id="00000000-0000-0000-0000-000000000000",
            dialogue_path=_DIALOGUE_BASE_PATH,
        ),
        method="POST",
        json=json_res,
        headers={"etag": _FAKE_ETAG},
    )

    res = await benerail_client.passengers_client.create_passenger(
        dialogue_id="00000000-0000-0000-0000-000000000000",
        etag="00000000-0000-0000-0000-000000000000",
        body=passenger.PassengerRequest(**json_req),
    )

    assert res.response_result.identifier == "00000000-0000-0000-0000-000000000000"


async def test_get_dialogue(
    httpx_mock: pytest_httpx.HTTPXMock,
    benerail_client: client.BenerailClient,
) -> None:
    json_res = conftest.load_file_fixture("get_dialogue.json")

    httpx_mock.add_response(
        url="{base_path}/{dialogue_path}/{dialogue_id}".format(
            base_path=conftest.API_BASE_URL,
            dialogue_path=_DIALOGUE_BASE_PATH,
            dialogue_id="00000000-0000-0000-0000-000000000000",
        ),
        method="GET",
        json=json_res,
        headers={"etag": _FAKE_ETAG},
    )

    dialogue = await benerail_client.dialogue.get_dialogue(
        dialogue_id="00000000-0000-0000-0000-000000000000",
    )

    assert dialogue.response_result.identifier == "00000000-0000-0000-0000-000000000000"


async def test_get_trip_offer(
    httpx_mock: pytest_httpx.HTTPXMock,
    benerail_client: client.BenerailClient,
) -> None:
    json_res = conftest.load_file_fixture("get_trip_offer.json")

    httpx_mock.add_response(
        url="{base_path}/{path}/trip-offers/{id}".format(
            base_path=conftest.API_BASE_URL,
            path=_TRIP_OFFER_PATH,
            id="00000000-0000-0000-0000-000000000000",
        ),
        method="GET",
        json=json_res,
    )

    res = await benerail_client.trip_offers_client.get_trip_offer_info(
        trip_offer_id="00000000-0000-0000-0000-000000000000",
    )

    assert res.response_result.identifier == "00000000-0000-0000-0000-000000000000"


async def test_get_offer(
    httpx_mock: pytest_httpx.HTTPXMock,
    benerail_client: client.BenerailClient,
) -> None:
    json_res = conftest.load_file_fixture("get_offer.json")

    httpx_mock.add_response(
        url="{base_path}/{path}/offers/{id}".format(
            base_path=conftest.API_BASE_URL,
            path=_TRIP_OFFER_PATH,
            id="00000000-0000-0000-0000-000000000000",
        ),
        method="GET",
        json=json_res,
    )

    res = await benerail_client.offers_client.get_offer_info(
        offer_id="00000000-0000-0000-0000-000000000000",
    )

    assert res.response_result.identifier == "00000000-0000-0000-0000-000000000000"
