import httpx

from snowfall.project.junction.go import fixtures
from snowfall.stdlib.integration.starlette import testing


class TestBookingsByOrder(object):
    async def test_bookings_are_found(self, client: httpx.AsyncClient) -> None:
        await testing.test_list_and_view_endpoints(
            client=client,
            url="/orders/{id}/bookings".format(id=fixtures.ORDERS[0]),
            expected_ids=[fixtures.BOOKINGS[0]],
        )


class TestBookingsDetailsByBooking(object):
    async def test_booking_details_are_found(self, client: httpx.AsyncClient) -> None:
        await testing.test_list_and_view_endpoints(
            client=client,
            url="/bookings/{id}/details".format(id=fixtures.BOOKINGS[0]),
            expected_ids=[fixtures.BOOKING_DETAILS[0]],
        )
