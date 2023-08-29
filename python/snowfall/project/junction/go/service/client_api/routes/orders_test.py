from typing import Any

import httpx
from starlette import status

from snowfall.project.junction.go import fixtures
from snowfall.stdlib.integration.starlette import testing


def _get_order_request() -> dict[str, Any]:
    return {
        "data": {
            "type": "orders",
            "attributes": {
                "passengers": [
                    {
                        "firstName": "First",
                        "lastName": "Last",
                        "title": "mr",
                        "gender": "male",
                        "dateOfBirth": "1970-12-23",
                    },
                ],
            },
            "relationships": {
                "quote": {
                    "data": {
                        "id": fixtures.PRICE_QUOTES[0],
                        "type": "trip-offer-price-quotes",
                    },
                },
            },
        },
    }


def _get_journey_request() -> dict[str, Any]:
    journey_request = _get_order_request()
    journey_request["data"]["attributes"]["contactDetails"] = {
        "email": "example@example.com",
        "phoneNumber": "+385996666666",
        "address": {
            "addressLines": [],
            "countryCode": "HR",
            "postalCode": "10000",
            "city": "Zagreb",
        },
    }

    return journey_request


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


class TestJourneys(object):
    async def test_journeys_are_found(self, client: httpx.AsyncClient) -> None:
        await testing.test_list_and_view_endpoints(
            client=client,
            url="/journeys",
            expected_ids=list(fixtures.JOURNEYS),
        )


class TestOrdersByJourney(object):
    async def test_orders_are_found(self, client: httpx.AsyncClient) -> None:
        await testing.test_list_and_view_endpoints(
            client=client,
            url="/journeys/{id}/orders".format(id=fixtures.JOURNEYS[0]),
            expected_ids=[fixtures.ORDERS[0]],
        )

    async def test_order_fails_for_unknown_journey(
        self,
        client: httpx.AsyncClient,
    ) -> None:
        response = await client.post(
            "/journeys/{id}/orders".format(id=fixtures.NOT_FOUND),
            json=_get_order_request(),
            headers={"Content-Type": "application/vnd.api+json"},
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND

    async def test_order_can_be_added_to_journey(
        self,
        client: httpx.AsyncClient,
    ) -> None:
        response = await client.post(
            "/journeys/{id}/orders".format(id=fixtures.JOURNEYS[1]),
            json=_get_order_request(),
            headers={"Content-Type": "application/vnd.api+json"},
        )

        assert response.status_code == status.HTTP_201_CREATED


class TestOrders(object):
    async def test_order_can_be_placed(self, client: httpx.AsyncClient) -> None:
        response = await client.post(
            "/orders",
            json=_get_journey_request(),
            headers={"Content-Type": "application/vnd.api+json"},
        )

        assert response.status_code == status.HTTP_201_CREATED


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
        cancellation_id = fixtures.BOOKINGS_CANCELLATION_REQUESTS[0]
        response = await client.get(
            "/bookings/cancellations/{id}".format(id=cancellation_id),
            headers={"Content-Type": "application/vnd.api+json"},
        )
        assert response.status_code == status.HTTP_200_OK

    async def test_bookings_cancellation_not_found(
        self,
        client: httpx.AsyncClient,
    ) -> None:
        response = await client.get(
            "/bookings/cancellations/{id}".format(id=fixtures.NOT_FOUND),
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND

    async def test_booking_cancellation_is_found_by_booking(
        self,
        client: httpx.AsyncClient,
    ) -> None:
        response = await client.get(
            "/bookings/{id}/cancellation".format(id=fixtures.BOOKINGS[0]),
        )

        assert response.status_code == status.HTTP_200_OK

    async def test_booking_cancellation_by_booking_not_found(
        self,
        client: httpx.AsyncClient,
    ) -> None:
        response = await client.get(
            "/bookings/{id}/cancellation".format(id=fixtures.NOT_FOUND),
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND


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
