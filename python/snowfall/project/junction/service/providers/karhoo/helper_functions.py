import zoneinfo

import timezonefinder

from snowfall.stdlib.v1.latlng_pb2 import LatLng

_tz_finder = timezonefinder.TimezoneFinder()


def get_zone_for_coordinate(coordinate: LatLng) -> zoneinfo.ZoneInfo:
    return zoneinfo.ZoneInfo(
        _tz_finder.timezone_at(
            lat=coordinate.latitude,
            lng=coordinate.longitude,
        )
        or "",
    )
