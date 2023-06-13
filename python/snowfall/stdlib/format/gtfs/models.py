import dataclasses
import datetime
from typing import Annotated

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
    agency_id: str | None
    agency_name: str
    agency_url: pydantic.HttpUrl
    agency_timezone: str
    agency_lang: str | None
    agency_phone: str | None
    agency_fare_url: pydantic.HttpUrl | None
    agency_email: pydantic.EmailStr | None

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
    default_lang: str | None
    feed_start_date: datetime.date | None
    feed_end_date: datetime.date | None
    feed_version: str | None
    feed_contact_email: pydantic.EmailStr | None
    feed_contact_url: pydantic.HttpUrl | None

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
    agency_id: str | None
    route_short_name: str | None
    route_long_name: str | None
    route_desc: str | None
    route_type: enums.RouteType
    route_url: pydantic.HttpUrl | None
    route_color: Annotated[str, pydantic.Field(regex=constants.COLOR_REGEX)] | None
    route_text_color: Annotated[str, pydantic.Field(regex=constants.COLOR_REGEX)] | None
    route_sort_order: pydantic.NonNegativeInt | None
    continuous_pickup: pydantic.NonNegativeInt | None
    continuous_drop_off: pydantic.NonNegativeInt | None


class Stop(_BaseModel):
    stop_id: str
    stop_code: str | None
    stop_name: str | None
    stop_desc: str | None
    stop_lat: Annotated[
        float,
        pydantic.Field(ge=constants.LATITUDE_MIN, le=constants.LATITUDE_MAX),
    ] | None
    stop_lon: Annotated[
        float,
        pydantic.Field(ge=constants.LONGITUDE_MIN, le=constants.LONGITUDE_MAX),
    ] | None
    zone_id: str | None
    stop_url: pydantic.HttpUrl | None
    location_type: enums.LocationType
    parent_station: str | None
    stop_timezone: str | None
    wheelchair_boarding: pydantic.NonNegativeInt = 0
    level_id: str | None
    platform_code: str | None

    _normalize_time_zone = normalizers.normalizer(
        ("stop_timezone",),
        normalizers.normalize_time_zone,
    )


class StopTime(_BaseModel):
    trip_id: str
    arrival_time: datetime.timedelta | None
    departure_time: datetime.timedelta | None
    stop_id: str
    stop_sequence: pydantic.NonNegativeInt
    stop_headsign: str | None
    pickup_type: enums.PickupType
    drop_off_type: enums.DropOffType
    continuous_pickup: pydantic.NonNegativeInt = 1
    continuous_drop_off: pydantic.NonNegativeInt = 1
    shape_dist_traveled: pydantic.NonNegativeFloat | None
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
    trip_headsign: str | None
    trip_short_name: str | None
    direction_id: pydantic.NonNegativeInt | None
    block_id: str | None
    shape_id: str | None
    wheelchair_accessible: pydantic.NonNegativeInt = 0
    bikes_allowed: pydantic.NonNegativeInt = 0


class Transfer(_BaseModel):
    from_stop_id: str
    to_stop_id: str
    transfer_type: int
    min_transfer_time: pydantic.NonNegativeInt | None


@dataclasses.dataclass(frozen=True)
class Feed(object):
    agencies: list[Agency]
    calendars: list[Calendar]
    calendar_dates: list[CalendarDate]
    feed_info: FeedInfo | None
    ref: str
    routes: list[Route]
    stops: list[Stop]
    stop_times: list[StopTime]
    trips: list[Trip]
