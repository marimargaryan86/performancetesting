import dataclasses
from collections.abc import Mapping, Sequence
from typing import Any

from starlette import status

from snowfall.project.junction.go.adapter import locations
from snowfall.project.junction.go.service.places.v1alpha import models_pb2, places_pb2
from snowfall.stdlib.format import protobuf
from snowfall.stdlib.integration.starlette import models


@dataclasses.dataclass(frozen=True)
class ValidationResult(object):
    errors: set[models.Error]
    locations: set[str]
    types: set[int]


async def validate_relationships(
    locations_client: locations.Client,
    payload: Mapping[str, Any],
) -> ValidationResult:
    place_types, place_errors = _validate_types(payload)
    # TODO: this should perhaps be done in the places service?
    location_ids, location_errors = await _validate_locations(
        locations_client,
        payload,
    )

    return ValidationResult(
        errors={*location_errors, *place_errors},
        locations=location_ids,
        types=place_types,
    )


async def _validate_locations(
    locations_client: locations.Client,
    payload: Mapping[str, Any],
) -> tuple[set[str], set[models.Error]]:
    wanted_locations: set[str] = set(payload.get("locations", []))

    if not wanted_locations:
        return set(), set()

    found_locations: set[str] = set()
    page = places_pb2.ListLocationsResponse()

    while True:
        page = await locations_client.find(
            identifiers=list(wanted_locations),
            cursor=page.next_page_token,
        )

        if not page.locations:
            break

        found_locations.update(location.id for location in page.locations)

    return found_locations, _find_missing_locations(
        list(payload["locations"]),
        frozenset(wanted_locations - found_locations),
    )


def _find_missing_locations(
    wanted_locations: Sequence[str],
    intersect_locations: frozenset[str],
) -> set[models.Error]:
    errors: set[models.Error] = set()
    for idx, location in enumerate(wanted_locations):
        if location in intersect_locations:
            errors.add(
                models.Error(
                    status=str(status.HTTP_404_NOT_FOUND),
                    code="not_found",
                    detail="'{0}' was not found".format(location),
                    source=models.ErrorSourcePointer(
                        pointer="/data/relationships/locations/data/{0}".format(
                            idx,
                        ),
                    ),
                ),
            )

    return errors


def _validate_types(
    payload: Mapping[str, Any],
) -> tuple[set[int], set[models.Error]]:
    place_types: set[int] = set()
    errors: set[models.Error] = set()

    for idx, place_type in enumerate(payload.get("types", [])):
        try:
            place_types.add(
                protobuf.slug_to_enum_value(
                    models_pb2.Location.Type,
                    place_type,
                ),
            )
        except ValueError:
            errors.add(
                models.Error(
                    status=str(status.HTTP_404_NOT_FOUND),
                    code="not_found",
                    detail="'{0}' was not found".format(place_type),
                    source=models.ErrorSourcePointer(
                        pointer="/data/relationships/types/data/{0}".format(idx),
                    ),
                ),
            )

    return place_types, errors
