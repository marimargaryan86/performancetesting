from typing import Any

import httpx
from starlette import status

from snowfall.project.junction.go import fixtures
from snowfall.stdlib.integration.starlette import testing


def _get_cancellation_request_request() -> dict[str, Any]:
    return {
        "data": {
            "type": "cancellation-request",
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


def _update_booking_cancellation_status_request() -> dict[str, Any]:
    return {
        "data": {
            "type": "booking-cancellation",
            "attributes": {
                "status": "completed",
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
    async def test_cancellation_request_creation(
        self,
        client: httpx.AsyncClient,
    ) -> None:
        response = await client.post(
            "/cancellation/request",
            json=_get_cancellation_request_request(),
            headers={"Content-Type": "application/vnd.api+json"},
        )

        assert response.status_code == status.HTTP_201_CREATED

    async def test_cancellation_request_retrieval(
        self,
        client: httpx.AsyncClient,
    ) -> None:
        response = await client.get(
            "/cancellation/request/{id}".format(
                id=fixtures.CANCELLATION_REQUESTS[0],
            ),
        )

        assert response.status_code == status.HTTP_200_OK

    async def test_booking_cancellation_are_found_by_booking(
        self,
        client: httpx.AsyncClient,
    ) -> None:
        response = await client.get(
            "/bookings/{id}/cancellation".format(id=fixtures.BOOKINGS[0]),
        )

        assert response.status_code == status.HTTP_200_OK

    async def test_booking_cancellation_status_can_be_updated(
        self,
        client: httpx.AsyncClient,
    ) -> None:
        response = await client.patch(
            "/bookings/cancellation/{id}".format(id=fixtures.BOOKING_CANCELLATIONS[0]),
            json=_update_booking_cancellation_status_request(),
            headers={"Content-Type": "application/vnd.api+json"},
        )

        assert response.status_code == status.HTTP_200_OK
