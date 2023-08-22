from typing import Any

import httpx
from starlette import status

from snowfall.project.junction.go import fixtures
from snowfall.stdlib.integration.starlette import testing


def _get_bookings_cancellation_request() -> dict[str, Any]:
    return {
        "data": {
            "type": "bookings-cancellations",
            "relationships": {
                "bookings": {
                    "data": [
                        {
                            "id": fixtures.BOOKINGS[0],
                            "type": "trip-bookings",
                        },
                    ],
                },
            },
        },
    }


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


class TestBookingsCancellation(object):
    async def test_bookings_can_be_cancelled(self, client: httpx.AsyncClient) -> None:
        response = await client.post(
            "/bookings/cancellations",
            json=_get_bookings_cancellation_request(),
            headers={"Content-Type": "application/vnd.api+json"},
        )

        assert response.status_code == status.HTTP_201_CREATED

    async def test_bookings_cancellation_retrieval(
        self,
        client: httpx.AsyncClient,
    ) -> None:
        response = await client.get(
            "/bookings/cancellations/{id}".format(
                id=fixtures.BOOKINGS_CANCELLATION_REQUESTS[0],
            ),
        )

        assert response.status_code == status.HTTP_200_OK
