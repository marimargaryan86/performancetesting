import httpx
from starlette import status

from snowfall import fixtures


class TestOrders(object):
    async def test_order_unauthorized(self, client: httpx.AsyncClient) -> None:
        client.headers["Authorization"] = "invalid"
        response = await client.get("/orders/{id}".format(id=fixtures.ORDERS[0]))
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_unknown_order_returns_not_found(
        self,
        client: httpx.AsyncClient,
    ) -> None:
        response = await client.get("/orders/{id}".format(id=fixtures.NOT_FOUND))
        assert response.status_code == status.HTTP_404_NOT_FOUND

    async def test_order_is_found(self, client: httpx.AsyncClient) -> None:
        response = await client.get("/orders/{id}".format(id=fixtures.ORDERS[0]))
        assert response.status_code == status.HTTP_200_OK

    async def test_order_creation_unauthorized(
        self,
        client: httpx.AsyncClient,
    ) -> None:
        client.headers["Authorization"] = "invalid"
        response = await client.post(
            "/orders",
            json={
                "data": {
                    "type": "orders",
                    "attributes": {
                        "offers": [
                            {
                                "offerAggregateId": fixtures.OFFERS[0],
                                "offerIds": [
                                    fixtures.PROVIDER_OFFERS[0],
                                ],
                                "passengers": [
                                    {
                                        "firstName": "First",
                                        "lastName": "Last",
                                        "title": "Mr",
                                        "gender": "male",
                                        "dateOfBirth": "1970-12-23",
                                    },
                                ],
                            },
                        ],
                        "contactDetails": {
                            "email": "example@example.com",
                            "phoneNumber": "+385996666666",
                            "address": {
                                "addressLines": [],
                                "countryCode": "HR",
                                "postalCode": "10000",
                                "city": "Zagreb",
                            },
                        },
                    },
                },
            },
            headers={"Content-Type": "application/vnd.api+json"},
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_offer_aggregate_id_is_not_found(
        self,
        client: httpx.AsyncClient,
    ) -> None:
        response = await client.post(
            "/orders",
            json={
                "data": {
                    "type": "orders",
                    "attributes": {
                        "offers": [
                            {
                                "offerAggregateId": fixtures.NOT_FOUND,
                                "offerIds": [
                                    fixtures.PROVIDER_OFFERS[0],
                                    fixtures.PROVIDER_OFFERS[2],
                                ],
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
                        ],
                        "contactDetails": {
                            "email": "example@example.com",
                            "phoneNumber": "+385996666666",
                            "address": {
                                "addressLines": [],
                                "countryCode": "HR",
                                "postalCode": "10000",
                                "city": "Zagreb",
                            },
                        },
                    },
                },
            },
            headers={"Content-Type": "application/vnd.api+json"},
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert response.json()["errors"][0][
            "detail"
        ] == "'{0}' was not found or has expired".format(fixtures.NOT_FOUND)

    async def test_order_can_be_created(
        self,
        client: httpx.AsyncClient,
    ) -> None:
        response = await client.post(
            "/orders",
            json={
                "data": {
                    "type": "orders",
                    "attributes": {
                        "offers": [
                            {
                                "offerAggregateId": fixtures.OFFERS[0],
                                "offerIds": [
                                    fixtures.PROVIDER_OFFERS[0],
                                    fixtures.PROVIDER_OFFERS[2],
                                ],
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
                        ],
                        "contactDetails": {
                            "email": "example@example.com",
                            "phoneNumber": "+385996666666",
                            "address": {
                                "addressLines": [],
                                "countryCode": "HR",
                                "postalCode": "10000",
                                "city": "Zagreb",
                            },
                        },
                    },
                },
            },
            headers={"Content-Type": "application/vnd.api+json"},
        )
        assert response.status_code == status.HTTP_201_CREATED

    async def test_offer_aggregate_ids_are_duplicated(
        self,
        client: httpx.AsyncClient,
    ) -> None:
        response = await client.post(
            "/orders",
            json={
                "data": {
                    "type": "orders",
                    "attributes": {
                        "offers": [
                            {
                                "offerAggregateId": fixtures.OFFERS[0],
                                "offerIds": [
                                    fixtures.PROVIDER_OFFERS[0],
                                    fixtures.PROVIDER_OFFERS[2],
                                ],
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
                            {
                                "offerAggregateId": fixtures.OFFERS[0],
                                "offerIds": [
                                    fixtures.PROVIDER_OFFERS[1],
                                    fixtures.PROVIDER_OFFERS[3],
                                ],
                                "passengers": [
                                    {
                                        "firstName": "First 2",
                                        "lastName": "Last 2",
                                        "title": "mr",
                                        "gender": "male",
                                        "dateOfBirth": "1970-12-23",
                                    },
                                ],
                            },
                        ],
                        "contactDetails": {
                            "email": "example@example.com",
                            "phoneNumber": "+385996666666",
                            "address": {
                                "addressLines": [],
                                "countryCode": "HR",
                                "postalCode": "10000",
                                "city": "Zagreb",
                            },
                        },
                    },
                },
            },
            headers={"Content-Type": "application/vnd.api+json"},
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert response.json()["errors"][0]["detail"] == "'{0}' is duplicated".format(
            fixtures.OFFERS[0],
        )

    async def test_offer_option_id_is_invalid(
        self,
        client: httpx.AsyncClient,
    ) -> None:
        response = await client.post(
            "/orders",
            json={
                "data": {
                    "type": "orders",
                    "attributes": {
                        "offers": [
                            {
                                "offerAggregateId": fixtures.OFFERS[0],
                                "offerIds": [
                                    fixtures.PROVIDER_OFFERS[0],
                                    fixtures.NOT_FOUND,
                                ],
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
                        ],
                        "contactDetails": {
                            "email": "example@example.com",
                            "phoneNumber": "+385996666666",
                            "address": {
                                "addressLines": [],
                                "countryCode": "HR",
                                "postalCode": "10000",
                                "city": "Zagreb",
                            },
                        },
                    },
                },
            },
            headers={"Content-Type": "application/vnd.api+json"},
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert response.json()["errors"][0][
            "detail"
        ] == "'{0}' is not a valid option for this offer".format(fixtures.NOT_FOUND)

    async def test_offer_option_id_missing_group(
        self,
        client: httpx.AsyncClient,
    ) -> None:
        response = await client.post(
            "/orders",
            json={
                "data": {
                    "type": "orders",
                    "attributes": {
                        "offers": [
                            {
                                "offerAggregateId": fixtures.OFFERS[0],
                                "offerIds": [fixtures.PROVIDER_OFFERS[0]],
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
                        ],
                        "contactDetails": {
                            "email": "example@example.com",
                            "phoneNumber": "+385996666666",
                            "address": {
                                "addressLines": [],
                                "countryCode": "HR",
                                "postalCode": "10000",
                                "city": "Zagreb",
                            },
                        },
                    },
                },
            },
            headers={"Content-Type": "application/vnd.api+json"},
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert response.json()["errors"][0][
            "detail"
        ] == "No option chosen for offer group '{0}'".format(fixtures.OFFER_GROUPS[1])

    async def test_offer_option_id_same_group(
        self,
        client: httpx.AsyncClient,
    ) -> None:
        response = await client.post(
            "/orders",
            json={
                "data": {
                    "type": "orders",
                    "attributes": {
                        "offers": [
                            {
                                "offerAggregateId": fixtures.OFFERS[0],
                                "offerIds": [
                                    fixtures.PROVIDER_OFFERS[0],
                                    fixtures.PROVIDER_OFFERS[1],
                                ],
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
                        ],
                        "contactDetails": {
                            "email": "example@example.com",
                            "phoneNumber": "+385996666666",
                            "address": {
                                "addressLines": [],
                                "countryCode": "HR",
                                "postalCode": "10000",
                                "city": "Zagreb",
                            },
                        },
                    },
                },
            },
            headers={"Content-Type": "application/vnd.api+json"},
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert response.json()["errors"][0][
            "detail"
        ] == "'{0}' belongs to the same group as another provided option".format(
            fixtures.PROVIDER_OFFERS[1],
        )

    async def test_order_amendment_unauthorized(
        self,
        client: httpx.AsyncClient,
    ) -> None:
        client.headers["Authorization"] = "invalid"
        response = await client.patch(
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
                                    fixtures.PROVIDER_OFFERS[0],
                                ],
                                "passengers": [
                                    {
                                        "firstName": "First",
                                        "lastName": "Last",
                                        "title": "Mr",
                                        "gender": "male",
                                        "dateOfBirth": "1970-12-23",
                                    },
                                ],
                            },
                        ],
                        "contactDetails": {
                            "email": "example@example.com",
                            "phoneNumber": "+385996666666",
                            "address": {
                                "addressLines": [],
                                "countryCode": "HR",
                                "postalCode": "10000",
                                "city": "Zagreb",
                            },
                        },
                    },
                },
            },
            headers={"Content-Type": "application/vnd.api+json"},
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_order_can_be_amended_with_existing_offer(
        self,
        client: httpx.AsyncClient,
    ) -> None:
        response = await client.patch(
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
                                    fixtures.PROVIDER_OFFERS[0],
                                ],
                                "passengers": [
                                    {
                                        "firstName": "First",
                                        "lastName": "Last",
                                        "title": "Mr",
                                        "gender": "male",
                                        "dateOfBirth": "1970-12-23",
                                    },
                                ],
                            },
                        ],
                        "contactDetails": {
                            "email": "example@example.com",
                            "phoneNumber": "+385996666666",
                            "address": {
                                "addressLines": [],
                                "countryCode": "HR",
                                "postalCode": "10000",
                                "city": "Zagreb",
                            },
                        },
                    },
                },
            },
            headers={"Content-Type": "application/vnd.api+json"},
        )
        assert response.status_code == status.HTTP_202_ACCEPTED
