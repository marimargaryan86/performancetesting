import pathlib
import uuid
import zipfile

import aiofiles
import geopy
import timezonefinder

from snowfall.junction.gtfs_feed import gtfs
from snowfall.transport import amqp

_NAMESPACE = uuid.UUID("5190984e-4ab7-411e-96f6-2848cc5d63e1")


async def process_places(
    geocoder: geopy.Photon,
    producer: amqp.Producer,
    tz_finder: timezonefinder.TimezoneFinder,
    feed_url: str,
    user_agent: str,
) -> None:
    async with aiofiles.tempfile.TemporaryDirectory() as tempdir:  # type: ignore[attr-defined]
        filename = pathlib.Path(tempdir, "feed.zip")

        await gtfs.fetch_feed(filename, feed_url, user_agent)

        with zipfile.ZipFile(filename) as zip_handle:
            if zip_handle.testzip():
                raise RuntimeError(
                    "{filename} is not a valid zip file".format(filename=str(filename)),
                )

            places = gtfs.unzip_stops(
                zip_handle,
                geocoder,
                tz_finder,
                uuid.uuid5(_NAMESPACE, feed_url),
                pathlib.Path(filename.parent, "stops.txt"),
            )

            async for place in places:
                await producer.publish(place, "place.import")
