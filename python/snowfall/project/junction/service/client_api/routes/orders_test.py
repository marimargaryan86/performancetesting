from typing import Any

import httpx
from starlette import status

from snowfall import fixtures
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
                "offer": {
                    "data": {
                        "id": fixtures.OFFERS[0],
                        "type": "offers",
                    },
                },
                "options": {
                    "data": [
                        {
                            "id": fixtures.PROVIDER_OFFERS[0],
                            "type": "offer-options",
                        },
                        {
                            "id": fixtures.PROVIDER_OFFERS[2],
                            "type": "offer-options",
                        },
                    ],
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

    async def test_order_with_unknown_offer_fails(
        self,
        client: httpx.AsyncClient,
    ) -> None:
        order = _get_journey_request()
        offer = order["data"]["relationships"]["offer"]
        offer["data"]["id"] = fixtures.NOT_FOUND

        response = await client.post(
            "/orders",
            json=order,
            headers={"Content-Type": "application/vnd.api+json"},
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert response.json()["errors"][0][
            "detail"
        ] == "'{0}' was not found or has expired".format(fixtures.NOT_FOUND)

    async def test_order_with_unknown_option_fails(
        self,
        client: httpx.AsyncClient,
    ) -> None:
        order = _get_journey_request()
        options = order["data"]["relationships"]["options"]
        options["data"][0]["id"] = fixtures.NOT_FOUND

        response = await client.post(
            "/orders",
            json=order,
            headers={"Content-Type": "application/vnd.api+json"},
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert response.json()["errors"][0][
            "detail"
        ] == "'{0}' is not a valid option for this offer".format(fixtures.NOT_FOUND)

    async def test_order_with_missing_group_fails(
        self,
        client: httpx.AsyncClient,
    ) -> None:
        order = _get_journey_request()
        options = order["data"]["relationships"]["options"]
        options["data"].pop()

        response = await client.post(
            "/orders",
            json=order,
            headers={"Content-Type": "application/vnd.api+json"},
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert response.json()["errors"][0][
            "detail"
        ] == "No option chosen for offer group '{0}'".format(fixtures.OFFER_GROUPS[1])

    async def test_order_with_option_from_same_group_fails(
        self,
        client: httpx.AsyncClient,
    ) -> None:
        order = _get_journey_request()
        options = order["data"]["relationships"]["options"]
        options["data"].append(
            {
                "id": fixtures.PROVIDER_OFFERS[1],
                "type": "offer-options",
            },
        )

        response = await client.post(
            "/orders",
            json=order,
            headers={"Content-Type": "application/vnd.api+json"},
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert response.json()["errors"][0][
            "detail"
        ] == "Multiple options chosen for group '{0}'".format(fixtures.OFFER_GROUPS[0])


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
