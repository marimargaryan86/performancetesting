import pytest_httpx

from snowfall.vendor.benerail import client, conftest

_BOOKING_BASE_PATH = "bookings/bookings"


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
    )

    booking = await benerail_client.bookings_client.get_booking(
        booking_id="00000000-0000-0000-0000-000000000000",
    )

    if booking.response_result:
        assert (
            booking.response_result.identifier == "00000000-0000-0000-0000-000000000000"
        )
