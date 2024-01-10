import datetime
import os
import uuid
from collections.abc import AsyncIterable, Sequence

from aiocsv import protocols, readers

from snowfall.project.junction.go.service.places import handlers, places
from snowfall.project.junction.go.service.places.typing import ProviderTypedDict
from snowfall.project.junction.go.service.places.v1 import models_pb2
from snowfall.stdlib import string
from snowfall.stdlib.format import protobuf
from snowfall.stdlib.v1 import latlng_pb2

_MIN_POPULATION = 20000
_NAMESPACE = uuid.UUID("105eba69-b787-48ba-9159-6078e0b76e46")
_MAX_AIRPORT_M = int(
    os.getenv("MAX_DISTANCE_AIRPORT_M", "50000"),  # noqa: WPS432
)
_MAX_RAIL_M = int(os.getenv("MAX_DISTANCE_RAIL_M", "10000"))  # noqa: WPS432


def _filter_location_by_type(
    locations: Sequence[models_pb2.Location],
    longitude: float,
    latitude: float,
) -> Sequence[str]:
    """Return filtered location IDs based on location.

    - Include railways only if < MAX_DISTANCE_RAIL_M from lat/lon
    - Include all Airports as the Mongo search already filters on MAX_DISTANCE_AIRPORT_M

    Assumes MAX_DISTANCE_AIRPORT_M >= MAX_DISTANCE_RAIL_M
    """
    valid_locations = []

    unconditional = {
        models_pb2.Location.Type.TYPE_AIRPORT,
        models_pb2.Location.Type.TYPE_CITY,
    }
    distance = {
        models_pb2.Location.Type.TYPE_RAILWAY_STATION,
        models_pb2.Location.Type.TYPE_FERRY_PORT,
        models_pb2.Location.Type.TYPE_BUS_STATION,
    }

    for location in locations:
        if unconditional.intersection(location.types):
            valid_locations.append(location.id)
        elif distance.intersection(location.types):
            loc = (location.coordinates.longitude, location.coordinates.latitude)
            if handlers.calculate_distance((longitude, latitude), loc) <= _MAX_RAIL_M:
                # It's close enough, add it.
                valid_locations.append(location.id)

    return valid_locations


async def parse_csv(  # noqa: WPS231
    locations_repository: places.LocationRepository,
    csv_file: protocols.WithAsyncRead,
    provider_jsons: ProviderTypedDict,
) -> AsyncIterable[models_pb2.Place]:
    async for row in readers.AsyncDictReader(csv_file):
        locations = [
            location
            async for location in await locations_repository.find_within_area(
                cursor="",
                latitude=float(row["latitude"]),
                longitude=float(row["longitude"]),
                max_distance_meters=_MAX_AIRPORT_M,
            )
            # TODO(jyggen): only locations in the same country
        ]

        location_ids = _filter_location_by_type(
            locations=locations,
            latitude=float(row["latitude"]),
            longitude=float(row["longitude"]),
        )

        if not location_ids:
            continue

        provider_places = []

        for provider in provider_jsons.values():
            for provider_id, json_bytes in provider.items():
                provider_data = handlers.find_nearest_provider_places(
                    provider_json=json_bytes,
                    coordinates=(float(row["latitude"]), float(row["longitude"])),
                    radius=_MAX_AIRPORT_M,
                )
                if provider_data:
                    provider_places.append((provider_id, provider_data))

        place_attributes = models_pb2.PlaceAttributes(
            provider_ids=[
                models_pb2.ProviderIds(
                    provider_id=provider_identifier,
                    place_ids=provider_place,
                )
                for provider_identifier, provider_place in provider_places
            ],
        )
        yield models_pb2.Place(
            merged_ids=location_ids,
            location=models_pb2.Location(
                id=string.to_uuid(row["id"], _NAMESPACE),
                name=row["name"],
                coordinates=latlng_pb2.LatLng(
                    latitude=float(row["latitude"]),
                    longitude=float(row["longitude"]),
                ),
                types=[models_pb2.Location.TYPE_CITY],
                updated_at=protobuf.datetime_to_protobuf(
                    datetime.datetime.now(tz=datetime.UTC),
                ),
                source_ref="cities",
            ),
            place_attributes=place_attributes,
        )
