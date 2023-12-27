# type: ignore  # noqa: PGH003
from collections.abc import Sequence

import pytest

from snowfall.project.junction.service.providers.benerail.stations import get_cities_ids
from snowfall.vendor.benerail.models.enumeration import response, results

cities_responses_examples: list[list[response.PlacesResponse]] = [
    [],
    [None],
    [response.PlacesResponse()],
    [response.PlacesResponse(response_result=None)],
    [
        response.PlacesResponse(
            response_result=response.PlacesResult(
                places=None,
            ),
        ),
    ],
    [
        response.PlacesResponse(
            response_result=response.PlacesResult(
                places=[],
            ),
        ),
    ],
    [
        response.PlacesResponse(
            response_result=response.PlacesResult(
                places=[
                    results.PlacesResult(identifier="place_id_1", name="Place 1"),
                    results.PlacesResult(identifier="place_id_2", name="Place 2"),
                ],
            ),
        ),
    ],
    [
        response.PlacesResponse(
            response_result=response.PlacesResult(
                places=[
                    results.PlacesResult(identifier="place_id_2", name=None),
                ],
            ),
        ),
    ],
    [
        None,
        response.PlacesResponse(response_result=None),
        response.PlacesResponse(
            response_result=results.PlacesResult(
                places=[
                    results.PlaceResult(identifier="place_id_2", name="Place 2"),
                    results.PlaceResult(identifier="place_id_3", name="Place 3"),
                ],
            ),
        ),
    ],
]


@pytest.mark.parametrize("cities_responses", cities_responses_examples)
async def test_get_cities_ids(
    cities_responses: Sequence[response.PlacesResponse],
) -> None:
    cities_ids = get_cities_ids(cities_responses)
    assert isinstance(cities_ids, set)
    for city_id in cities_ids:
        assert isinstance(city_id, str)
