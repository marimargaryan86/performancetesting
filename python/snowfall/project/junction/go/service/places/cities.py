import datetime
import math
import os
import uuid
from collections.abc import AsyncIterable, Sequence

from aiocsv import protocols, readers

from snowfall.project.junction.go.service.places import places
from snowfall.project.junction.go.service.places.v1 import models_pb2
from snowfall.stdlib import string
from snowfall.stdlib.format import protobuf
from snowfall.stdlib.logging import stdout
from snowfall.stdlib.v1 import latlng_pb2

_MIN_POPULATION = 20000
_NAMESPACE = uuid.UUID("105eba69-b787-48ba-9159-6078e0b76e46")
_MAX_DISTANCE_AIRPORT_M = int(
    os.getenv("MAX_DISTANCE_AIRPORT_M", "50000"),  # noqa: WPS432
)
_MAX_DISTANCE_RAIL_M = int(os.getenv("MAX_DISTANCE_RAIL_M", "10000"))  # noqa: WPS432


def _calculate_distance(
    p1: tuple[float, float],
    p2: tuple[float, float],
) -> float:
    """Return the great circle distance in meters between two points."""
    lon1, lat1, lon2, lat2 = map(math.radians, (*p1, *p2))

    dlon = math.sin((lon2 - lon1) / 2) ** 2
    dlat = math.sin((lat2 - lat1) / 2) ** 2
    hav = dlat + math.cos(lat1) * math.cos(lat2) * dlon
    distance = 2 * math.asin(math.sqrt(hav))
    radius_of_earth_in_metres = 6371000
    return distance * radius_of_earth_in_metres


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
            if _calculate_distance((longitude, latitude), loc) <= _MAX_DISTANCE_RAIL_M:
                # It's close enough, add it.
                valid_locations.append(location.id)

    return valid_locations


async def parse_csv(
    locations_repository: places.LocationRepository,
    csv_file: protocols.WithAsyncRead,
) -> AsyncIterable[models_pb2.Place]:
    logger = stdout.get_logger()
    async for row in readers.AsyncDictReader(csv_file):
        locations = [
            location
            async for location in await locations_repository.find_within_area(
                cursor="",
                latitude=float(row["latitude"]),
                longitude=float(row["longitude"]),
                max_distance_meters=_MAX_DISTANCE_AIRPORT_M,
            )
            # TODO: only locations in the same country
        ]

        location_ids = _filter_location_by_type(
            locations=locations,
            latitude=float(row["latitude"]),
            longitude=float(row["longitude"]),
        )

        if not location_ids:
            logger.warning(
                "Place (city) has no known locations",
                name=row["name"],
            )
            continue

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
        )
