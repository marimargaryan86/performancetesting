import datetime
import functools
from typing import Generator, Sequence

import pydantic
import timezonefinder

from snowfall.stdlib.format.gtfs import enums as gtfs_enums
from snowfall.stdlib.format.gtfs import models as gtfs_models
from snowfall.vendor.direct_ferries.models import route as df_route_models
from snowfall.vendor.direct_ferries.models import timetable as df_timetable_models

_DEPARTURE_ARRIVAL = ("departure", "arrival")
_AGENCY_ID = "Direct-Ferries"
_AGENCY_NAME = "Direct Ferries"
_AGENCY_URL = "https://www.directferries.com/"
_URL_HOST = "directferries.com"
_URL_SCHEME = "https"
_AGENCY_TIMEZONE = "utc"
_FEED_PUBLISHER_NAME = "Direct Ferries"
_FEED_LANG = "en"
_EXCEPTION_TYPE = 1
_TRANSFER_TYPE = 0


@functools.lru_cache(maxsize=100)
def _timedelta_to_time(td: datetime.timedelta) -> str:
    day_hours, minutes_seconds = str(
        datetime.timedelta(seconds=td.seconds),
    ).split(":", maxsplit=1)

    real_hours = int(day_hours) + 24 * td.days

    return ":".join([str(real_hours), minutes_seconds])


class StopTimeFields(pydantic.BaseModel):
    departure: datetime.datetime
    arrival: datetime.datetime
    drop_off_type: gtfs_enums.DropOffType
    pickup_type: gtfs_enums.PickupType
    stop_code: str
    stop_sequence: int


class DFDataConverter(object):  # noqa: WPS214
    def __init__(
        self,
        timetable_responses: Sequence[df_timetable_models.TimetableResponse],
    ):
        self._timetable_responses = timetable_responses
        self._calendar_dates_mapping: dict[int, str] = {}

        self._tz_finder = timezonefinder.TimezoneFinder()

    def convert_agency(self) -> Generator[gtfs_models.Agency, None, None]:
        yield gtfs_models.Agency(
            agency_id=_AGENCY_ID,
            agency_name=_AGENCY_NAME,
            agency_url=pydantic.HttpUrl(
                _AGENCY_URL,
                scheme=_URL_SCHEME,
                host=_URL_HOST,
            ),
            agency_timezone=_AGENCY_TIMEZONE,
        )

    def convert_feed_info(self) -> Generator[gtfs_models.FeedInfo, None, None]:
        yield gtfs_models.FeedInfo(
            feed_publisher_name=_FEED_PUBLISHER_NAME,
            feed_publisher_url=pydantic.HttpUrl(
                _AGENCY_URL,
                scheme=_URL_SCHEME,
                host=_URL_HOST,
            ),
            feed_lang=_FEED_LANG,
        )

    def convert_stops(self) -> Generator[gtfs_models.Stop, None, None]:
        existing_stops = set()

        for timetable_response in self._timetable_responses:
            ports = [
                timetable_response.route.port_from,
                timetable_response.route.port_to,
            ]
            for port in ports:
                if port.code not in existing_stops:
                    existing_stops.add(port.code)

                    yield gtfs_models.Stop(
                        stop_id=port.code,
                        stop_name=port.name,
                        stop_lat=port.latitude,
                        stop_lon=port.longitude,
                        location_type=gtfs_enums.LocationType.platform,
                        stop_timezone=self._tz_finder.timezone_at(
                            lat=port.latitude,
                            lng=port.longitude,
                        ),
                    )

    def convert_routes(self) -> Generator[gtfs_models.Route, None, None]:
        route_identifiers = set()

        for timetable_response in self._timetable_responses:
            route_identifier = "{0}-{1}".format(
                timetable_response.route.port_from.code,
                timetable_response.route.port_to.code,
            ).strip()
            if route_identifier not in route_identifiers:
                route_identifiers.add(route_identifier)
                yield gtfs_models.Route(
                    route_id=str(timetable_response.route.route_id),
                    agency_id=_AGENCY_ID,
                    route_long_name=timetable_response.route.name,
                    route_short_name=route_identifier,
                    route_type=gtfs_enums.RouteType.ferry,
                )

    def convert_trips(self) -> Generator[gtfs_models.Trip, None, None]:
        for timetable_response in self._timetable_responses:
            for operator_tt in timetable_response.timetable_data.operator_timetables:
                for timetable in operator_tt.timetables:
                    trip_id = "{0}-{1}-{2}-{3}".format(
                        operator_tt.operator_id,
                        timetable_response.route.route_id,
                        timetable.departure_time.isoformat(),
                        timetable.arrival_time.isoformat(),
                    )

                    yield gtfs_models.Trip(
                        route_id=str(timetable_response.route.route_id),
                        service_id=trip_id,
                        trip_id=trip_id,
                    )

    def convert_stop_times(self) -> Generator[gtfs_models.StopTime, None, None]:
        for timetable_response in self._timetable_responses:
            for operator_tt in timetable_response.timetable_data.operator_timetables:
                for date in operator_tt.timetables:
                    yield gtfs_models.StopTime(
                        trip_id="{0}-{1}-{2}-{3}".format(
                            operator_tt.operator_id,
                            timetable_response.route.route_id,
                            date.departure_time.isoformat(),
                            date.arrival_time.isoformat(),
                        ),
                        departure_time=datetime.timedelta(
                            hours=date.departure_time.hour,
                            minutes=date.departure_time.minute,
                            seconds=date.departure_time.second,
                        ),
                        arrival_time=datetime.timedelta(
                            hours=date.departure_time.hour,
                            minutes=date.departure_time.minute,
                            seconds=date.departure_time.second,
                        ),
                        stop_id=timetable_response.route.port_from.code,
                        stop_sequence=1,
                        pickup_type=gtfs_enums.PickupType.regularly_scheduled_pickup,
                        drop_off_type=gtfs_enums.DropOffType.no_drop_off_available,
                    )

                    yield gtfs_models.StopTime(
                        trip_id="{0}-{1}-{2}-{3}".format(
                            operator_tt.operator_id,
                            timetable_response.route.route_id,
                            date.departure_time.isoformat(),
                            date.arrival_time.isoformat(),
                        ),
                        departure_time=datetime.timedelta(
                            hours=date.arrival_time.hour,
                            minutes=date.arrival_time.minute,
                            seconds=date.arrival_time.second,
                        ),
                        arrival_time=datetime.timedelta(
                            hours=date.arrival_time.hour,
                            minutes=date.arrival_time.minute,
                            seconds=date.arrival_time.second,
                        ),
                        stop_id=timetable_response.route.port_to.code,
                        stop_sequence=2,
                        pickup_type=gtfs_enums.PickupType.regularly_scheduled_pickup,
                        drop_off_type=gtfs_enums.DropOffType.no_drop_off_available,
                    )

    def convert_calendar_dates(self) -> Generator[gtfs_models.CalendarDate, None, None]:
        yield from (  # noqa: WPS224
            gtfs_models.CalendarDate(
                service_id="{0}-{1}-{2}-{3}".format(
                    operator_tt.operator_id,
                    timetable_response.route.route_id,
                    tt.departure_time.isoformat(),
                    tt.arrival_time.isoformat(),
                ),
                date=tt.departure_time.strftime(  # type: ignore[arg-type]
                    "%Y%m%d",
                ),
                exception_type=_EXCEPTION_TYPE,
            )
            for timetable_response in self._timetable_responses
            for operator_tt in timetable_response.timetable_data.operator_timetables
            for tt in operator_tt.timetables
        )

    def convert_transfers(self) -> Generator[gtfs_models.Transfer, None, None]:
        route_identifiers = set()

        for timetable_response in self._timetable_responses:
            route_identifier = "{0}-{1}".format(
                timetable_response.route.port_from.code,
                timetable_response.route.port_to.code,
            ).strip()

            if route_identifier not in route_identifiers:
                route_identifiers.add(route_identifier)

                yield gtfs_models.Transfer(
                    from_stop_id=timetable_response.route.port_from.code,
                    to_stop_id=timetable_response.route.port_to.code,
                    transfer_type=_TRANSFER_TYPE,
                )

    def stop_time_fields(
        self,
        time_type: str,
        date: df_timetable_models.Timetable,
        route: df_route_models.Route,
    ) -> StopTimeFields:
        """stop_sequence: Order of stops for a particular trip.

        The values must increase along the trip but do not need to be consecutive.
        For direct trips we will have two options here 1 and 2
        """
        if time_type == "departure":
            return StopTimeFields(
                departure=date.departure_time,
                arrival=date.departure_time,
                drop_off_type=gtfs_enums.DropOffType.no_drop_off_available,
                pickup_type=gtfs_enums.PickupType.regularly_scheduled_pickup,
                stop_code=route.port_from.code,
                stop_sequence=1,
            )
        return StopTimeFields(
            departure=date.arrival_time,
            arrival=date.arrival_time,
            drop_off_type=gtfs_enums.DropOffType.regularly_scheduled_drop_off,
            pickup_type=gtfs_enums.PickupType.no_pickup_available,
            stop_code=route.port_to.code,
            stop_sequence=2,
        )
