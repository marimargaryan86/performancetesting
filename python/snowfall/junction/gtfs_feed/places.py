import pathlib
import uuid

import aiofiles
import tenacity
from geopy import exc

from snowfall.common.v1alpha import models_pb2
from snowfall.format.gtfs import feed
from snowfall.geodata import geocoding
from snowfall.junction.gtfs_feed import gtfs
from snowfall.transport import amqp

_NAMESPACE = uuid.UUID("5190984e-4ab7-411e-96f6-2848cc5d63e1")


async def process_places(
    geocoder: geocoding.ReverseGeocoder,
    producer: amqp.Producer,
    feed_url: str,
    user_agent: str,
) -> None:
    async with aiofiles.tempfile.TemporaryDirectory() as tempdir:  # type: ignore[attr-defined]
        filename = pathlib.Path(tempdir, "feed.zip")

        await gtfs.fetch_feed(filename, feed_url, user_agent)

        async for stop in (await feed.load_from_zip(filename)).stops:
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
                            id=str(uuid.uuid5(_NAMESPACE, stop.stop_id)),
                            name=stop.stop_name or "",
                            latitude=stop.stop_lat,
                            longitude=stop.stop_lon,
                            country_code=(
                                await geocoder.get_country_code(
                                    latitude=stop.stop_lat,
                                    longitude=stop.stop_lon,
                                )
                            ),
                            time_zone=await geocoder.get_time_zone(
                                latitude=stop.stop_lat,
                                longitude=stop.stop_lon,
                            ),
                        ),
                        "place.import",
                    )
