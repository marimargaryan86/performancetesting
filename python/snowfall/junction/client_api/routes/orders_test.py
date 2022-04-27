import pytest
from starlette import status, testclient

from snowfall import fixtures


@pytest.mark.asyncio
class TestOrders(object):
    async def test_unknown_order_returns_not_found(
        self,
        client: testclient.TestClient,
    ) -> None:
        response = client.get("/orders/{id}".format(id=fixtures.NOT_FOUND))
        assert response.status_code == status.HTTP_404_NOT_FOUND

    async def test_order_is_found(self, client: testclient.TestClient) -> None:
        response = client.get("/orders/{id}".format(id=fixtures.ORDERS[0]))
        assert response.status_code == status.HTTP_200_OK

    async def test_order_unknown_offer_returns_error(
        self,
        client: testclient.TestClient,
    ) -> None:
        response = client.post(
            "/orders",
            json={
                "data": {
                    "type": "orders",
                    "attributes": {
                        "offers": [
                            {
                                "offerAggregateId": fixtures.NOT_FOUND,
                                "offerIds": [
                                    fixtures.OFFERS[0],
                                ],
                            },
                        ],
                    },
                },
            },
            headers={"Content-Type": "application/vnd.api+json"},
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    async def test_order_can_be_created(
        self,
        client: testclient.TestClient,
    ) -> None:
        response = client.post(
            "/orders",
            json={
                "data": {
                    "type": "orders",
                    "attributes": {
                        "offers": [
                            {
                                "offerAggregateId": fixtures.OFFERS[0],
                                "offerIds": [
                                    fixtures.OFFERS[0],
                                ],
                            },
                        ],
                    },
                },
            },
            headers={"Content-Type": "application/vnd.api+json"},
        )
        assert response.status_code == status.HTTP_201_CREATED

    async def test_order_cant_be_amended_with_unexisting_offer(
        self,
        client: testclient.TestClient,
    ) -> None:
        response = client.patch(
            "/orders/{orderId}".format(
                orderId=fixtures.ORDERS[0],
            ),
            json={
                "data": {
                    "type": "orders",
                    "attributes": {
                        "offers": [
                            {
                                "offerAggregateId": fixtures.NOT_FOUND,
                                "offerIds": [
                                    fixtures.OFFERS[0],
                                ],
                            },
                        ],
                    },
                },
            },
            headers={"Content-Type": "application/vnd.api+json"},
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    async def test_order_can_be_amended_with_existing_offer(
        self,
        client: testclient.TestClient,
    ) -> None:
        response = client.patch(
            "/orders/{orderId}".format(
                orderId=fixtures.ORDERS[0],
            ),
            json={
                "data": {
                    "type": "orders",
                    "attributes": {
                        "offers": [
                            {
                                "offerAggregateId": fixtures.OFFERS[0],
                                "offerIds": [
                                    fixtures.OFFERS[0],
                                ],
                            },
                        ],
                    },
                },
            },
            headers={"Content-Type": "application/vnd.api+json"},
        )
        assert response.status_code == status.HTTP_202_ACCEPTED
