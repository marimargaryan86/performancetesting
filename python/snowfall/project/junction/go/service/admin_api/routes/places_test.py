import random
from typing import Any

import httpx
from starlette import status

from snowfall.project.junction.go import fixtures
from snowfall.stdlib.integration.starlette import testing


async def test_places(client: httpx.AsyncClient) -> None:
    await testing.test_list_and_view_endpoints(
        client=client,
        url="/places",
        expected_ids=fixtures.PLACES,
    )


async def test_create_place(client: httpx.AsyncClient) -> None:
    expected_resource = {
        "type": "places",
        "attributes": {
            "name": "Foobar",
            "latitude": random.uniform(*fixtures.LATITUDE_RANGE),  # noqa: S311
            "longitude": random.uniform(*fixtures.LONGITUDE_RANGE),  # noqa: S311
        },
        "relationships": {
            "locations": {
                "data": [
                    {"id": fixtures.LOCATIONS[0], "type": "locations"},
                ],
            },
            "types": {
                "data": [
                    {"id": "unspecified", "type": "place-types"},
                ],
            },
        },
    }
    response = await client.post(
        url="/places",
        json={
            "data": expected_resource,
        },
        headers={"Content-Type": "application/vnd.api+json"},
    )

    assert response.status_code == status.HTTP_201_CREATED

    created_resource: dict[str, Any] = response.json()["data"]

    assert testing.resource_is_subset(expected_resource, created_resource)
    await testing.test_resource_is_fetchable(client, created_resource)


async def test_create_place_invalid_relationships(client: httpx.AsyncClient) -> None:
    expected_resource = {
        "type": "places",
        "attributes": {
            "name": "Foobar",
            "latitude": random.uniform(*fixtures.LATITUDE_RANGE),  # noqa: S311
            "longitude": random.uniform(*fixtures.LONGITUDE_RANGE),  # noqa: S311
        },
        "relationships": {
            "locations": {
                "data": [
                    {"id": fixtures.LOCATIONS[0], "type": "locations"},
                    {"id": fixtures.NOT_FOUND, "type": "locations"},
                ],
            },
            "types": {
                "data": [
                    {"id": "unspecified", "type": "place-types"},
                    {"id": fixtures.NOT_FOUND, "type": "place-types"},
                ],
            },
        },
    }
    response = await client.post(
        url="/places",
        json={
            "data": expected_resource,
        },
        headers={"Content-Type": "application/vnd.api+json"},
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


async def test_delete_place(client: httpx.AsyncClient) -> None:
    response = await client.delete(
        url="/places/{place_id}".format(place_id=fixtures.PLACES[0]),
        headers={"Content-Type": "application/vnd.api+json"},
    )

    assert response.status_code == status.HTTP_204_NO_CONTENT


async def test_update_place(client: httpx.AsyncClient) -> None:
    expected_resource = {
        "type": "places",
        "attributes": {
            "name": "Foobar",
            "latitude": random.uniform(*fixtures.LATITUDE_RANGE),  # noqa: S311
            "longitude": random.uniform(*fixtures.LONGITUDE_RANGE),  # noqa: S311
        },
        "relationships": {
            "locations": {
                "data": [
                    {"id": fixtures.LOCATIONS[0], "type": "locations"},
                ],
            },
            "types": {
                "data": [
                    {"id": "unspecified", "type": "place-types"},
                ],
            },
        },
    }
    response = await client.patch(
        url="/places/{place_id}".format(place_id=fixtures.PLACES[0]),
        json={
            "data": expected_resource,
        },
        headers={"Content-Type": "application/vnd.api+json"},
    )

    assert response.status_code == status.HTTP_200_OK

    updated_resource: dict[str, Any] = response.json()["data"]

    await testing.test_resource_is_fetchable(client, updated_resource)
