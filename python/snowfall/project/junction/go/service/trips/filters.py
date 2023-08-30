import asyncio
from collections.abc import Sequence

from snowfall.project.junction.go.service.trips import cache
from snowfall.project.junction.go.v1 import models_pb2

_metadata_retrieval_semaphore = asyncio.Semaphore(3)


async def _get_for_trip(
    trip_reference: models_pb2.TripReference,
    trip_metadata_repository: cache.TripMetadataRepository,
) -> cache.TripMetadata:
    async with _metadata_retrieval_semaphore:
        return await trip_metadata_repository.get_for_trip(trip_reference)


async def filter_trip_references(
    trip_references: Sequence[models_pb2.TripReference],
    trip_metadata_repository: cache.TripMetadataRepository,
    max_trip_length_factor: float,
) -> list[models_pb2.TripReference]:
    metadata_objects = await asyncio.gather(
        *[
            _get_for_trip(trip_reference, trip_metadata_repository)
            for trip_reference in trip_references
        ],
    )
    trip_metadata_map = {metadata.identifier: metadata for metadata in metadata_objects}
    shortest_trip = min(metadata_objects, key=lambda metadata: metadata.duration)
    shortest_duration = shortest_trip.duration

    return [
        trip_reference
        for trip_reference in trip_references
        if trip_metadata_map[trip_reference.id].is_multimodal
        or trip_metadata_map[trip_reference.id].duration / shortest_duration
        < max_trip_length_factor
    ]
