import uuid

import tenacity
from geopy import exc

from snowfall.common.v1alpha import latlng_pb2, models_pb2
from snowfall.junction.gtfs_feed import importer
from snowfall.service.geodata.v1 import geocoding_pb2, geocoding_pb2_grpc
from snowfall.stdlib.transport import amqp

_NAMESPACE = uuid.UUID("5190984e-4ab7-411e-96f6-2848cc5d63e1")


async def process_places(
    geocoder: geocoding_pb2_grpc.GeocodingServiceStub,
    producer: amqp.Producer,
    collection: importer.RepositoryCollection,
    ref: str,
) -> None:
    namespace = uuid.uuid5(_NAMESPACE, ref)

    async for stop in await collection.stops.all_():
        if not stop.stop_lat or not stop.stop_lon or stop.parent_station:
            continue

        retry = tenacity.Retrying(
            retry=tenacity.retry_if_exception_type(exc.GeocoderTimedOut),
            wait=tenacity.wait_random_exponential(multiplier=1, max=60),
        )

        for attempt in retry:
            with attempt:
                await producer.publish(
                    models_pb2.Place(
                        id=str(
                            uuid.uuid5(
                                namespace,
                                stop.stop_id,
                            ),
                        ),
                        name=stop.stop_name or "",
                        coordinates=models_pb2.Coordinates(
                            latitude=stop.stop_lat,
                            longitude=stop.stop_lon,
                        ),
                        country_code=(
                            await geocoder.CountryCodeLookup(
                                geocoding_pb2.CountryCodeLookupRequest(
                                    coordinates=latlng_pb2.LatLng(
                                        latitude=stop.stop_lat,
                                        longitude=stop.stop_lon,
                                    ),
                                ),
                            )
                        ).country_code,
                        time_zone=(
                            await geocoder.TimeZoneLookup(
                                geocoding_pb2.TimeZoneLookupRequest(
                                    coordinates=latlng_pb2.LatLng(
                                        latitude=stop.stop_lat,
                                        longitude=stop.stop_lon,
                                    ),
                                ),
                            )
                        ).time_zone.id,
                        source_ref=ref,
                    ),
                    "place.import",
                )
