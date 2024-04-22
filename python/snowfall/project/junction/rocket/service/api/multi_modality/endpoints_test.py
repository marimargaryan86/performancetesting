import datetime
from collections.abc import Mapping
from typing import Any

import httpx
import pytest
from starlette import status

from snowfall.project.junction.rocket import fixtures
from snowfall.project.junction.rocket.service.api.multi_modality import repository


@pytest.fixture()
def generation() -> datetime.timedelta:
    return datetime.timedelta(weeks=52 * 20)


@pytest.fixture()
def now() -> datetime.datetime:
    return datetime.datetime.now(tz=datetime.UTC)


@pytest.fixture()
def date_of_birth(
    now: datetime.datetime,
    generation: datetime.timedelta,
) -> datetime.date:
    return now.date() - generation


@pytest.fixture()
def tomorrow(now: datetime.datetime) -> datetime.datetime:
    return now + datetime.timedelta(days=1)


@pytest.fixture()
def yesterday(now: datetime.datetime) -> datetime.datetime:
    return now - datetime.timedelta(days=1)


@pytest.fixture()
def valid_payload(
    tomorrow: datetime.datetime,
    date_of_birth: datetime.date,
) -> dict[str, Any]:
    return {
        "data": {
            "type": "journey-suggestion-searches",
            "attributes": {
                "departureAfter": tomorrow.isoformat(),
                "passengers": [
                    {
                        "dateOfBirth": date_of_birth.isoformat(),
                    },
                ],
            },
            "relationships": {
                "origin": {
                    "data": {
                        "id": fixtures.PLACES[0],
                        "type": "places",
                    },
                },
                "destination": {
                    "data": {
                        "id": fixtures.PLACES[0],
                        "type": "places",
                    },
                },
            },
        },
    }


def assert_pointer(error: Mapping[str, Any], pointer: str) -> None:
    assert error["source"]["pointer"] == pointer


class TestGetSuggestion:
    async def test_unknown_search_id_is_not_found(
        self,
        client: httpx.AsyncClient,
    ) -> None:
        response = await client.get(
            url="/journeys/suggestions/{0}".format(fixtures.NOT_FOUND),
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND

    async def test_known_search_id_is_found(
        self,
        client: httpx.AsyncClient,
        suggestion_repository: repository.SuggestionRepository,
    ) -> None:
        suggestion = await suggestion_repository.create()
        response = await client.get(
            url="/journeys/suggestions/{0}".format(suggestion.id),
        )
        assert response.status_code == status.HTTP_200_OK


class TestCreateSuggestionSearch:
    async def test_unknown_origin_fails(
        self,
        client: httpx.AsyncClient,
        valid_payload: Mapping[str, Any],
    ) -> None:
        origin = valid_payload["data"]["relationships"]["origin"]
        origin["data"]["id"] = fixtures.NOT_FOUND
        response = await client.post(
            url="/journeys/suggestions/searches",
            json=valid_payload,
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        errors = response.json()["errors"]
        assert len(errors) == 1
        assert_pointer(errors[0], "/data/relationships/origin/data/id")

    async def test_unknown_destination_fails(
        self,
        client: httpx.AsyncClient,
        valid_payload: Mapping[str, Any],
    ) -> None:
        destination = valid_payload["data"]["relationships"]["destination"]
        destination["data"]["id"] = fixtures.NOT_FOUND
        response = await client.post(
            url="/journeys/suggestions/searches",
            json=valid_payload,
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        errors = response.json()["errors"]
        assert len(errors) == 1
        assert_pointer(errors[0], "/data/relationships/destination/data/id")

    async def test_unborn_passenger_fails(
        self,
        client: httpx.AsyncClient,
        valid_payload: Mapping[str, Any],
        tomorrow: datetime.datetime,
    ) -> None:
        passengers = valid_payload["data"]["attributes"]["passengers"]
        passengers[0]["dateOfBirth"] = tomorrow.date().isoformat()
        response = await client.post(
            url="/journeys/suggestions/searches",
            json=valid_payload,
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        errors = response.json()["errors"]
        assert len(errors) == 1
        assert_pointer(errors[0], "/data/attributes/passengers/0/dateOfBirth")

    async def test_past_departure_fails(
        self,
        client: httpx.AsyncClient,
        valid_payload: Mapping[str, Any],
        yesterday: datetime.datetime,
    ) -> None:
        attributes = valid_payload["data"]["attributes"]
        attributes["departureAfter"] = yesterday.isoformat()
        response = await client.post(
            url="/journeys/suggestions/searches",
            json=valid_payload,
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        errors = response.json()["errors"]
        assert len(errors) == 1
        assert_pointer(errors[0], "/data/attributes/departureAfter")

    async def test_search_is_successfully_created(
        self,
        client: httpx.AsyncClient,
        valid_payload: Mapping[str, Any],
    ) -> None:
        response = await client.post(
            url="/journeys/suggestions/searches",
            json=valid_payload,
        )
        assert response.status_code == status.HTTP_201_CREATED

    async def test_self_link_works(
        self,
        client: httpx.AsyncClient,
        valid_payload: Mapping[str, Any],
    ) -> None:
        create_response = await client.post(
            url="/journeys/suggestions/searches",
            json=valid_payload,
        )
        create_response_data = create_response.json()
        self_link = create_response_data["data"]["links"]["self"]
        get_response = await client.get(url=self_link)
        assert get_response.status_code == status.HTTP_200_OK


class TestGetSuggestionSearch:
    async def test_unknown_search_id_is_not_found(
        self,
        client: httpx.AsyncClient,
    ) -> None:
        response = await client.get(
            url="/journeys/suggestions/searches/{0}".format(fixtures.NOT_FOUND),
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND

    async def test_known_search_id_is_found(
        self,
        client: httpx.AsyncClient,
        valid_payload: Mapping[str, Any],
    ) -> None:
        create_response = await client.post(
            url="/journeys/suggestions/searches",
            json=valid_payload,
        )
        create_response_data = create_response.json()
        search_id = create_response_data["data"]["id"]
        get_response = await client.get(
            url="/journeys/suggestions/searches/{0}".format(search_id),
        )
        assert get_response.status_code == status.HTTP_200_OK
