import uuid
from typing import AsyncIterable

from aiocsv import AsyncDictReader, protocols

from snowfall.project.junction.service.places import places
from snowfall.project.junction.service.places.v1alpha import models_pb2
from snowfall.stdlib import string
from snowfall.stdlib.v1alpha import latlng_pb2

_MIN_POPULATION = 20000
_MAX_DISTANCE = 50000  # todo: differentiate between airports and train stations
_NAMESPACE = uuid.UUID("105eba69-b787-48ba-9159-6078e0b76e46")


async def parse_csv(
    locations_repository: places.LocationRepository,
    csv_file: protocols.WithAsyncRead,
) -> AsyncIterable[models_pb2.Place]:
    async for row in AsyncDictReader(csv_file):
        if int(float(row["population"] or 0)) < _MIN_POPULATION:
            continue

        location_ids = [
            location.id
            async for location in await locations_repository.find_within_area(
                cursor="",
                latitude=float(row["lat"]),
                longitude=float(row["lng"]),
                max_distance_meters=_MAX_DISTANCE,
            )
            # todo: only locations in the same country
        ]

        if not location_ids:
            continue

        yield models_pb2.Place(
            merged_ids=location_ids,
            location=models_pb2.Location(
                id=string.to_uuid(row["id"], _NAMESPACE),
                name=row["city"],
                coordinates=latlng_pb2.LatLng(
                    latitude=float(row["lat"]),
                    longitude=float(row["lng"]),
                ),
                types=[models_pb2.Location.TYPE_CITY],
            ),
        )
