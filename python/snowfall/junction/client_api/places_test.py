import uuid

import pytest

from snowfall.junction.client_api import conftest, places


@pytest.mark.asyncio
async def test_single_place_is_retrievable(
    place_repository: places.PlaceRepository,
) -> None:
    identifier = conftest.PLACES[0]["id"]
    place = await place_repository.get(uuid.UUID(identifier))
    assert str(place.identifier) == identifier


@pytest.mark.asyncio
async def test_missing_place_throws_error(
    place_repository: places.PlaceRepository,
) -> None:
    with pytest.raises(places.NotFoundError):
        await place_repository.get(uuid.UUID(conftest.PLACE_NOT_FOUND))


@pytest.mark.asyncio
async def test_multiple_places_are_retrievable(
    place_repository: places.PlaceRepository,
) -> None:
    found_places = await place_repository.find()
    assert len(found_places) == 2
    assert str(found_places[0].identifier) == conftest.PLACES[0]["id"]
    assert str(found_places[1].identifier) == conftest.PLACES[1]["id"]
