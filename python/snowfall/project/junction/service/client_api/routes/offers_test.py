from typing import Sequence

import pytest
import rapidjson
from starlette import status, testclient

from snowfall import fixtures
from snowfall.stdlib.integration.starlette.routes import testing


@pytest.mark.asyncio
class TestOffers(object):
    async def test_unknown_offer_returns_not_found(
        self,
        client: testclient.TestClient,
    ) -> None:
        response = client.get("/offers/{id}".format(id=fixtures.NOT_FOUND))
        assert response.status_code == status.HTTP_404_NOT_FOUND

    async def test_offer_is_found(self, client: testclient.TestClient) -> None:
        response = client.get("/offers/{id}".format(id=fixtures.OFFERS[0]))
        assert response.status_code == status.HTTP_200_OK

    async def test_offer_unauthorized(self, client: testclient.TestClient) -> None:
        client.headers["Authorization"] = "invalid"
        response = client.get("/offers/{id}".format(id=fixtures.OFFERS[0]))
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio
class TestOfferGroups(object):
    async def test_unknown_offer_group_returns_not_found(
        self,
        client: testclient.TestClient,
    ) -> None:
        response = client.get("/offers/groups/{id}".format(id=fixtures.NOT_FOUND))
        assert response.status_code == status.HTTP_404_NOT_FOUND

    async def test_offer_group_is_found(self, client: testclient.TestClient) -> None:
        response = client.get("/offers/groups/{id}".format(id=fixtures.OFFER_GROUPS[0]))
        assert response.status_code == status.HTTP_200_OK

    async def test_offer_groups_by_offer(self, client: testclient.TestClient) -> None:
        testing.test_list_and_view_endpoints(
            client=client,
            url="/offers/{id}/groups".format(id=fixtures.OFFERS[0]),
            expected_ids=fixtures.OFFER_GROUPS,
        )


@pytest.mark.asyncio
class TestOfferGroupDetails(object):
    async def test_unknown_offer_group_details_returns_not_found(
        self,
        client: testclient.TestClient,
    ) -> None:
        response = client.get(
            "/offers/groups/details/{id}".format(id=fixtures.NOT_FOUND),
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND

    async def test_offer_group_is_found(self, client: testclient.TestClient) -> None:
        response = client.get(
            "/offers/groups/details/{id}".format(id=fixtures.OFFER_GROUP_DETAILS[0]),
        )
        assert response.status_code == status.HTTP_200_OK

    async def test_offer_group_details_by_offer_group(
        self,
        client: testclient.TestClient,
    ) -> None:
        testing.test_list_and_view_endpoints(
            client=client,
            url="/offers/groups/{id}/details".format(id=fixtures.OFFER_GROUPS[0]),
            expected_ids=fixtures.OFFER_GROUP_DETAILS,
        )


@pytest.mark.asyncio
class TestOfferOptions(object):
    async def test_unknown_offer_option_returns_not_found(
        self,
        client: testclient.TestClient,
    ) -> None:
        response = client.get(
            "/offers/options/{id}".format(id=fixtures.NOT_FOUND),
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND

    async def test_offer_group_is_found(self, client: testclient.TestClient) -> None:
        response = client.get(
            "/offers/options/{id}".format(id=fixtures.PROVIDER_OFFERS[0]),
        )
        assert response.status_code == status.HTTP_200_OK

    async def test_offer_options_by_offer_group(
        self,
        client: testclient.TestClient,
    ) -> None:
        testing.test_list_and_view_endpoints(
            client=client,
            url="/offers/groups/{id}/options".format(id=fixtures.OFFER_GROUPS[0]),
            expected_ids=fixtures.PROVIDER_OFFERS,
        )


@pytest.mark.asyncio
class TestOfferOptionDetails(object):
    async def test_unknown_offer_option_details_returns_not_found(
        self,
        client: testclient.TestClient,
    ) -> None:
        response = client.get(
            "/offers/options/details/{id}".format(id=fixtures.NOT_FOUND),
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND

    async def test_offer_group_is_found(self, client: testclient.TestClient) -> None:
        response = client.get(
            "/offers/options/details/{id}".format(id=fixtures.OFFER_DETAILS[0]),
        )
        assert response.status_code == status.HTTP_200_OK

    async def test_offer_option_details_by_offer_option(
        self,
        client: testclient.TestClient,
    ) -> None:
        testing.test_list_and_view_endpoints(
            client=client,
            url="/offers/options/{id}/details".format(id=fixtures.PROVIDER_OFFERS[0]),
            expected_ids=fixtures.OFFER_DETAILS,
        )


@pytest.mark.asyncio
class TestOfferSearches(object):
    async def test_offer_search_unauthorized(
        self,
        client: testclient.TestClient,
    ) -> None:
        client.headers["Authorization"] = "invalid"
        response = client.post(
            "/offers/searches",
            json={
                "data": {
                    "type": "trip-offer-searches",
                    "attributes": {
                        "passengers": [
                            {
                                "dateOfBirth": "1979-09-17",
                            },
                        ],
                    },
                    "relationships": {
                        "trips": {
                            "data": [
                                {
                                    "id": fixtures.TRIPS[0],
                                    "type": "trips",
                                },
                            ],
                        },
                    },
                },
            },
            headers={"Content-Type": "application/vnd.api+json"},
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_offer_search_unknown_trip_returns_error(
        self,
        client: testclient.TestClient,
    ) -> None:
        response = client.post(
            "/offers/searches",
            json={
                "data": {
                    "type": "trip-offer-searches",
                    "attributes": {
                        "passengers": [
                            {
                                "dateOfBirth": "1979-09-17",
                            },
                        ],
                    },
                    "relationships": {
                        "trips": {
                            "data": [
                                {
                                    "id": fixtures.NOT_FOUND,
                                    "type": "trips",
                                },
                            ],
                        },
                    },
                },
            },
            headers={"Content-Type": "application/vnd.api+json"},
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND

    async def test_offer_search_can_be_created(
        self,
        client: testclient.TestClient,
    ) -> None:
        response = client.post(
            "/offers/searches",
            json={
                "data": {
                    "type": "trip-offer-searches",
                    "attributes": {
                        "passengers": [
                            {
                                "dateOfBirth": "1979-09-17",
                            },
                        ],
                    },
                    "relationships": {
                        "trips": {
                            "data": [
                                {
                                    "id": fixtures.TRIPS[0],
                                    "type": "trips",
                                },
                            ],
                        },
                    },
                },
            },
            headers={"Content-Type": "application/vnd.api+json"},
        )
        assert response.status_code == status.HTTP_201_CREATED

    async def test_created_trip_offer_search_can_be_retrieved(
        self,
        client: testclient.TestClient,
    ) -> None:
        offer_search = client.post(
            "/offers/searches",
            json={
                "data": {
                    "type": "trip-offer-searches",
                    "attributes": {
                        "passengers": [
                            {
                                "dateOfBirth": "1979-09-17",
                            },
                        ],
                    },
                    "relationships": {
                        "trips": {
                            "data": [
                                {
                                    "id": fixtures.TRIPS[0],
                                    "type": "trips",
                                },
                            ],
                        },
                    },
                },
            },
            headers={"Content-Type": "application/vnd.api+json"},
        )
        offer_search_id = rapidjson.loads(offer_search.content.decode())["data"]["id"]
        response = client.get(
            "/offers/searches/{id}".format(id=offer_search_id),
        )
        assert response.status_code == status.HTTP_200_OK

    async def test_created_trip_offer_search_unauthorized(
        self,
        client: testclient.TestClient,
    ) -> None:
        offer_search = client.post(
            "/offers/searches",
            json={
                "data": {
                    "type": "trip-offer-searches",
                    "attributes": {
                        "passengers": [
                            {
                                "dateOfBirth": "1979-09-17",
                            },
                        ],
                    },
                    "relationships": {
                        "trips": {
                            "data": [
                                {
                                    "id": fixtures.TRIPS[0],
                                    "type": "trips",
                                },
                            ],
                        },
                    },
                },
            },
            headers={"Content-Type": "application/vnd.api+json"},
        )
        offer_search_id = rapidjson.loads(offer_search.content.decode())["data"]["id"]
        client.headers["Authorization"] = "invalid"
        response = client.get(
            "/offers/searches/{id}".format(id=offer_search_id),
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_unknown_offer_search_returns_not_found(
        self,
        client: testclient.TestClient,
    ) -> None:
        response = client.get(
            "/offers/searches/{id}/offers".format(
                id=fixtures.NOT_FOUND,
            ),
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND

    async def test_offers_are_found(
        self,
        client: testclient.TestClient,
    ) -> None:
        response = client.get(
            "/offers/searches/{id}/offers".format(
                id=fixtures.OFFER_SEARCHES[0],
            ),
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["data"]

    @pytest.mark.parametrize(
        "cabin_classes, expected",
        [
            (["economy"], 1),
            (["economy", "business"], 1),
            (["business"], 0),
            (["unknown"], 0),
            (["economy", "unknown"], 1),
        ],
    )
    async def test_cabin_class_filter(
        self,
        client: testclient.TestClient,
        cabin_classes: Sequence[str],
        expected: int,
    ) -> None:
        response = client.get(
            "/offers/searches/{id}/offers".format(
                id=fixtures.OFFER_SEARCHES[0],
            ),
            params=[
                ("filter[groups.options.details.cabinClass]", ",".join(cabin_classes)),
            ],
        )
        assert len(response.json()["data"]) == expected
