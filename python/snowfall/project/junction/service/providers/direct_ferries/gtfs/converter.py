import datetime
import typing

import pydantic

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
        timetables_data: typing.Sequence[df_timetable_models.TimeTable],
    ):
        self._timetables_data = timetables_data
        self._calendar_dates_mapping: dict[int, str] = {}

    def convert_agency(self) -> typing.Sequence[gtfs_models.Agency]:
        return [
            gtfs_models.Agency(
                agency_id=_AGENCY_ID,
                agency_name=_AGENCY_NAME,
                agency_url=pydantic.HttpUrl(
                    _AGENCY_URL,
                    scheme=_URL_SCHEME,
                    host=_URL_HOST,
                ),
                agency_timezone=_AGENCY_TIMEZONE,
            ),
        ]

    def convert_feed_info(self) -> typing.Sequence[gtfs_models.FeedInfo]:
        return [
            gtfs_models.FeedInfo(
                feed_publisher_name=_FEED_PUBLISHER_NAME,
                feed_publisher_url=pydantic.HttpUrl(
                    _AGENCY_URL,
                    scheme=_URL_SCHEME,
                    host=_URL_HOST,
                ),
                feed_lang=_FEED_LANG,
            ),
        ]

    def convert_stops(self) -> typing.Sequence[gtfs_models.Stop]:
        existing_stops = set()
        stops = []
        for timetable in self._timetables_data:
            ports = [timetable.route.port_from, timetable.route.port_to]
            for port in ports:
                if port.code not in existing_stops:
                    existing_stops.add(port.code)
                    stops.append(
                        gtfs_models.Stop(
                            stop_id=port.code,
                            stop_name=port.name,
                            stop_lat=port.latitude,
                            stop_lon=port.longitude,
                            location_type=gtfs_enums.LocationType.platform,
                        ),
                    )
        return stops

    def convert_routes(self) -> typing.Sequence[gtfs_models.Route]:
        route_identifiers = set()
        routes = []
        for timetable in self._timetables_data:
            route_identifier = "{0}-{1}".format(
                timetable.route.port_from.code,
                timetable.route.port_to.code,
            ).strip()
            if route_identifier not in route_identifiers:
                route_identifiers.add(route_identifier)
                routes.append(
                    gtfs_models.Route(
                        route_id=str(timetable.route.route_id),
                        agency_id=_AGENCY_ID,
                        route_long_name=timetable.route.name,
                        route_short_name=route_identifier,
                        route_type=gtfs_enums.RouteType.ferry,
                    ),
                )
        return routes

    def convert_trips(self) -> typing.Sequence[gtfs_models.Trip]:  # noqa: WPS210
        trips = []
        service_id = 0
        for timetable in self._timetables_data:
            for date in timetable.timetables:
                trip_id = "{0}-{1}-{2}-{3}".format(
                    timetable.route.operator_details.identifier,
                    timetable.route.route_id,
                    date.departure_time,
                    date.arrival_time,
                )
                for time_type in _DEPARTURE_ARRIVAL:
                    service_id = service_id + 1
                    trips.append(
                        gtfs_models.Trip(
                            route_id="{0}-{1}".format(
                                timetable.route.port_from.code,
                                timetable.route.port_to.code,
                            ),
                            service_id=str(service_id),
                            trip_id=trip_id,
                        ),
                    )
                    self._calendar_dates_mapping[service_id] = (
                        date.departure_time.strftime("%Y%m%d")
                        if time_type == "departure"
                        else date.arrival_time.strftime("%Y%m%d")
                    )

        return trips

    def convert_stop_times(self) -> typing.Sequence[gtfs_models.StopTime]:
        stop_times = []
        for timetable in self._timetables_data:
            for date in timetable.timetables:
                for time_type in _DEPARTURE_ARRIVAL:
                    fields = self.stop_time_fields(
                        time_type=time_type,
                        date=date,
                        route=timetable.route,
                    )
                    stop_times.append(
                        gtfs_models.StopTime(
                            trip_id="{0}-{1}-{2}-{3}".format(
                                timetable.route.operator_details.identifier,
                                timetable.route.route_id,
                                date.departure_time,
                                date.arrival_time,
                            ),
                            departure_time=datetime.timedelta(
                                hours=fields.departure.hour,
                                minutes=fields.departure.minute,
                                seconds=fields.departure.second,
                            ),
                            arrival_time=datetime.timedelta(
                                hours=fields.arrival.hour,
                                minutes=fields.arrival.minute,
                                seconds=fields.arrival.second,
                            ),
                            stop_id=fields.stop_code,
                            stop_sequence=fields.stop_sequence,
                            pickup_type=fields.pickup_type,
                            drop_off_type=fields.drop_off_type,
                        ),
                    )
        return stop_times

    def convert_calendar_dates(self) -> typing.Sequence[gtfs_models.CalendarDate]:
        calendar_dates = []
        service_id = 0
        for timetable in self._timetables_data:
            for _ in timetable.timetables:
                service_id += 1
                calendar_date = gtfs_models.CalendarDate(
                    service_id=str(service_id),
                    date=self._calendar_dates_mapping[service_id],  # type: ignore[arg-type]
                    exception_type=_EXCEPTION_TYPE,
                )
                calendar_dates.append(calendar_date)
        return calendar_dates

    def convert_transfers(self) -> typing.Sequence[gtfs_models.Transfer]:
        transfers = []
        route_identifiers = []
        for timetable in self._timetables_data:
            route_identifier = "{0}-{1}".format(
                timetable.route.port_from.code,
                timetable.route.port_to.code,
            ).strip()
            if route_identifier not in route_identifiers:
                route_identifiers.append(route_identifier)
                transfer = gtfs_models.Transfer(
                    from_stop_id=timetable.route.port_from.code,
                    to_stop_id=timetable.route.port_to.code,
                    transfer_type=_TRANSFER_TYPE,
                )
                transfers.append(transfer)
        return transfers

    def stop_time_fields(
        self,
        time_type: str,
        date: df_timetable_models.TimetableData,
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
