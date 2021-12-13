import uuid

import pytest

from snowfall.junction.places import places


@pytest.mark.asyncio
async def test_single_place_is_retrievable() -> None:
    repository = places.PlaceRepository()
    identifier = uuid.UUID("f236a92c-4cfa-468e-85ef-431d25dcd925")
    place = await repository.get(identifier)

    assert place.identifier == identifier


@pytest.mark.asyncio
async def test_missing_place_throws_error() -> None:
    repository = places.PlaceRepository()

    with pytest.raises(places.NotFoundError):
        await repository.get(uuid.uuid4())


@pytest.mark.asyncio
async def test_multiple_places_are_retrievable() -> None:
    repository = places.PlaceRepository()
    found_places = await repository.find()

    assert len(found_places) == 2
    assert all(
        identifier in {place.identifier for place in found_places}
        for identifier in (
            uuid.UUID("f236a92c-4cfa-468e-85ef-431d25dcd925"),
            uuid.UUID("488a836d-ec22-439b-a9d8-3c4c386a731e"),
        )
    )
