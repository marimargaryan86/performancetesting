import dataclasses
import datetime
from typing import Annotated, Optional

import pydantic

from snowfall.stdlib.format.gtfs import constants, enums, normalizers


def _timedelta_to_time(td: datetime.timedelta) -> str:
    day_hours, minutes_seconds = str(
        datetime.timedelta(seconds=td.seconds),
    ).split(":", maxsplit=1)

    real_hours = int(day_hours) + 24 * td.days

    return ":".join([str(real_hours), minutes_seconds])


class _BaseModel(pydantic.BaseModel):
    class Config(object):
        json_encoders = {
            datetime.date: lambda date_obj: date_obj.strftime("%Y%m%d"),
            datetime.timedelta: _timedelta_to_time,
        }


class Agency(_BaseModel):
    agency_id: Optional[str]
    agency_name: str
    agency_url: pydantic.HttpUrl
    agency_timezone: str
    agency_lang: Optional[str]
    agency_phone: Optional[str]
    agency_fare_url: Optional[pydantic.HttpUrl]
    agency_email: Optional[pydantic.EmailStr]

    _normalize_language_code = normalizers.normalizer(
        ("agency_lang",),
        normalizers.normalize_language_code,
    )
    _normalize_phone_number = normalizers.normalizer(
        ("agency_phone",),
        normalizers.normalize_phone_number,
    )
    _normalize_time_zone = normalizers.normalizer(
        ("agency_timezone",),
        normalizers.normalize_time_zone,
    )


class Calendar(_BaseModel):
    service_id: str
    monday: bool
    tuesday: bool
    wednesday: bool
    thursday: bool
    friday: bool
    saturday: bool
    sunday: bool
    start_date: datetime.date
    end_date: datetime.date

    _normalize_date = normalizers.normalizer(
        ("start_date", "end_date"),
        normalizers.normalize_date,
    )


class CalendarDate(_BaseModel):
    service_id: str
    date: datetime.date
    exception_type: Annotated[int, pydantic.Field(ge=1, le=2)]

    _normalize_date = normalizers.normalizer(("date",), normalizers.normalize_date)


class FeedInfo(_BaseModel):
    feed_publisher_name: str
    feed_publisher_url: pydantic.HttpUrl
    feed_lang: str
    default_lang: Optional[str]
    feed_start_date: Optional[datetime.date]
    feed_end_date: Optional[datetime.date]
    feed_version: Optional[str]
    feed_contact_email: Optional[pydantic.EmailStr]
    feed_contact_url: Optional[pydantic.HttpUrl]

    _normalize_date = normalizers.normalizer(
        (
            "feed_start_date",
            "feed_end_date",
        ),
        normalizers.normalize_date,
    )
    _normalize_language_code = normalizers.normalizer(
        (
            "feed_lang",
            "default_lang",
        ),
        normalizers.normalize_language_code,
    )


class Route(_BaseModel):
    route_id: str
    agency_id: Optional[str]
    route_short_name: Optional[str]
    route_long_name: Optional[str]
    route_desc: Optional[str]
    route_type: enums.RouteType
    route_url: Optional[pydantic.HttpUrl]
    route_color: Optional[Annotated[str, pydantic.Field(regex=constants.COLOR_REGEX)]]
    route_text_color: Optional[
        Annotated[str, pydantic.Field(regex=constants.COLOR_REGEX)]
    ]
    route_sort_order: Optional[pydantic.NonNegativeInt]
    continuous_pickup: Optional[pydantic.NonNegativeInt]
    continuous_drop_off: Optional[pydantic.NonNegativeInt]


class Stop(_BaseModel):
    stop_id: str
    stop_code: Optional[str]
    stop_name: Optional[str]
    stop_desc: Optional[str]
    stop_lat: Optional[
        Annotated[
            float,
            pydantic.Field(ge=constants.LATITUDE_MIN, le=constants.LATITUDE_MAX),
        ]
    ]
    stop_lon: Optional[
        Annotated[
            float,
            pydantic.Field(ge=constants.LONGITUDE_MIN, le=constants.LONGITUDE_MAX),
        ]
    ]
    zone_id: Optional[str]
    stop_url: Optional[pydantic.HttpUrl]
    location_type: enums.LocationType
    parent_station: Optional[str]
    stop_timezone: Optional[str]
    wheelchair_boarding: pydantic.NonNegativeInt = 0
    level_id: Optional[str]
    platform_code: Optional[str]

    _normalize_time_zone = normalizers.normalizer(
        ("stop_timezone",),
        normalizers.normalize_time_zone,
    )


class StopTime(_BaseModel):
    trip_id: str
    arrival_time: Optional[datetime.timedelta]
    departure_time: Optional[datetime.timedelta]
    stop_id: str
    stop_sequence: pydantic.NonNegativeInt
    stop_headsign: Optional[str]
    pickup_type: enums.PickupType
    drop_off_type: enums.DropOffType
    continuous_pickup: pydantic.NonNegativeInt = 1
    continuous_drop_off: pydantic.NonNegativeInt = 1
    shape_dist_traveled: Optional[pydantic.NonNegativeFloat]
    timepoint: pydantic.NonNegativeInt = 1

    _normalize_time = normalizers.normalizer(
        (
            "arrival_time",
            "departure_time",
        ),
        normalizers.normalize_time,
    )


class Trip(_BaseModel):
    route_id: str
    service_id: str
    trip_id: str
    trip_headsign: Optional[str]
    trip_short_name: Optional[str]
    direction_id: Optional[pydantic.NonNegativeInt]
    block_id: Optional[str]
    shape_id: Optional[str]
    wheelchair_accessible: pydantic.NonNegativeInt = 0
    bikes_allowed: pydantic.NonNegativeInt = 0


class Transfer(_BaseModel):
    from_stop_id: str
    to_stop_id: str
    transfer_type: int
    min_transfer_time: Optional[pydantic.NonNegativeInt]


@dataclasses.dataclass(frozen=True)
class Feed(object):
    agencies: list[Agency]
    calendars: list[Calendar]
    calendar_dates: list[CalendarDate]
    feed_info: Optional[FeedInfo]
    ref: str
    routes: list[Route]
    stops: list[Stop]
    stop_times: list[StopTime]
    trips: list[Trip]
