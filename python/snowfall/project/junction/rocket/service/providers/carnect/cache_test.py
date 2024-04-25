import datetime

from bson.tz_util import utc

from snowfall.project.junction.go.v1 import models_pb2 as common_pb2
from snowfall.project.junction.rocket.service.providers.carnect import cache, criteria
from snowfall.stdlib.v1 import latlng_pb2


def test_generate_cache_key_is_correct() -> None:
    search = criteria.Criteria(
        search_id="7556d31c-1a35-40e7-a748-04fe7d3d4d49",
        origin=common_pb2.Point(
            ref="test_ref",
            name="Point name",
            coordinates=latlng_pb2.LatLng(
                latitude=46.287961,
                longitude=11.232652,
            ),
            time_zone="Europe/Stockholm",
        ),
        destination=common_pb2.Point(
            ref="test_ref",
            name="Point name",
            coordinates=latlng_pb2.LatLng(
                latitude=55.287961,
                longitude=56.232652,
            ),
            time_zone="Europe/Stockholm",
        ),
        pickup_datetime=datetime.datetime(
            year=2024,
            month=12,
            day=12,
            hour=14,
            second=0,
            microsecond=0,
            tzinfo=utc,
        ),
        return_datetime=datetime.datetime(
            year=2024,
            month=12,
            day=12,
            hour=14,
            second=0,
            microsecond=0,
            tzinfo=utc,
        ),
        driver_age=32,
    )

    cache_key = cache.generate_cache_key(search)

    assert cache_key == "57ee9314-5567-5610-aa78-c9fbd0fb1a5e"
