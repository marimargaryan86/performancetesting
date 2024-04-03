import datetime
import json
from collections.abc import Iterable, Sequence
from typing import NamedTuple

from snowfall.project.junction.content.service.direct_ferries import (
    parsers,
    port,
    routes,
)
from snowfall.project.junction.provider.v2alpha import trips_pb2
from snowfall.project.junction.v1 import fare_type_pb2, segment_type_pb2
from snowfall.stdlib import h3
from snowfall.stdlib.format import protobuf
from snowfall.stdlib.time import date_to_age
from snowfall.stdlib.v1 import latlng_pb2
from snowfall.vendor.direct_ferries import client
from snowfall.vendor.direct_ferries.models import leg, passenger, quote, request

_CURRENCY = "EUR"


class CabinClass(NamedTuple):
    cabin_type: fare_type_pb2.FareType.ValueType
    marketing_name: str


class Transformer:
    def __init__(self, h3_port_mapping: h3.H3MappingRepository[port.Port]):
        self._h3_port_mapping = h3_port_mapping

    def to_results(
        self,
        quote_results: Sequence[quote.Quote],
    ) -> list[trips_pb2.Result]:
        results = {}
        for quote_result in quote_results:
            result = trips_pb2.Result(
                base_amount=parsers.amount_to_proto(
                    amount=str(quote_result.price.total_in_selected_currency),
                    currency=quote_result.selected_currency,
                ),
                total_amount=parsers.amount_to_proto(
                    amount=str(quote_result.price.total_in_selected_currency),
                    currency=quote_result.selected_currency,
                ),
                # TODO(artur.m): check for tax amount in df api
                trips=[
                    self.trip_to_proto(result_leg) for result_leg in quote_result.legs
                ],
            )
            results[calculate_result_hash(result)] = result
        return list(results.values())

    def trip_to_proto(self, result_leg: leg.Leg) -> trips_pb2.Trip:
        return trips_pb2.Trip(
            segments=self.segment_to_proto(result_leg),
            fare=trips_pb2.Trip.Fare(),
        )

    def segment_to_proto(
        self,
        result_leg: leg.Leg,
    ) -> list[trips_pb2.Segment]:
        departure_port = self._get_port_from_ports(result_leg.departure_port_code)
        arrival_port = self._get_port_from_ports(result_leg.arrival_port_code)

        return [
            trips_pb2.Segment(
                origin=trips_pb2.Location(
                    ref=str(result_leg.departure_port_id),
                    name=result_leg.departure_port_name,
                    coordinates=latlng_pb2.LatLng(
                        longitude=departure_port.longitude,
                        latitude=departure_port.latitude,
                    ),
                ),
                destination=trips_pb2.Location(
                    ref=str(result_leg.arrival_port_id),
                    name=result_leg.arrival_port_name,
                    coordinates=latlng_pb2.LatLng(
                        longitude=arrival_port.longitude,
                        latitude=arrival_port.latitude,
                    ),
                ),
                departure_at=protobuf.datetime_to_protobuf_datetime(
                    result_leg.departure_date_time.replace(
                        tzinfo=departure_port.timezone,
                    ),
                ),
                arrival_at=protobuf.datetime_to_protobuf_datetime(
                    result_leg.arrival_date_time.replace(tzinfo=arrival_port.timezone),
                ),
                stops=[],
                type=segment_type_pb2.SEGMENT_TYPE_FERRY,
                marketed_by=trips_pb2.Segment.Company(
                    # TODO(artur.m): check if df has similar property
                ),
                operated_by=trips_pb2.Segment.Company(
                    route_number=str(result_leg.route_id),
                    code=str(result_leg.operator.identifier) or "",
                    name=result_leg.operator.name,
                ),
                vehicle=self._ship_to_proto(result_leg),
                passengers=[
                    self._passenger_to_proto(passenger)
                    for passenger in result_leg.passengers
                ],
            ),
        ]

    def _get_port_from_ports(self, port_id: str) -> port.Port:
        for ports in self._h3_port_mapping._mapping.values():  # noqa: SLF001
            for mapped_port in ports:
                if mapped_port.identifier == port_id:
                    return mapped_port
        raise ValueError("Invalid port id")

    def _ship_to_proto(
        self,
        result_leg: leg.Leg,
    ) -> trips_pb2.Segment.Vehicle | None:
        return trips_pb2.Segment.Vehicle(
            # TODO(artur.m): check is there ship id in df response?
            name=result_leg.ship.name,
        )

    def _passenger_to_proto(
        self,
        trip_passenger: passenger.Passenger,
    ) -> trips_pb2.Segment.Passenger:
        # TODO(artur.m): check df api docs for passenger type
        return trips_pb2.Segment.Passenger(
            seating=trips_pb2.Segment.Passenger.Seating(
                type=fare_type_pb2.FARE_TYPE_UNSPECIFIED,
            ),
        )


def _datetime_to_utc_without_tz(date_time: datetime.datetime) -> datetime.datetime:
    return date_time.astimezone(datetime.UTC).replace(tzinfo=None)


class Trips:
    def __init__(
        self,
        search_client: client.DfHttpClient,
        transformer: Transformer,
        route_repo: routes.RouteRepository,
        h3_port_mapping: h3.H3MappingRepository[port.Port],
    ):
        self._client = search_client
        self._transformer = transformer
        self._route = route_repo
        self._h3_port_mapping = h3_port_mapping

    async def find_one_way(
        self,
        trip_request: trips_pb2.SearchTripsRequest.OneWay,
        passengers: Iterable[trips_pb2.SearchTripsRequest.Passenger],
    ) -> trips_pb2.SearchTripsResponse:
        result: Sequence[quote.Quote] = await self._client.quotes.get_quotes(
            request=self.one_way_to_offer_request(trip_request, passengers),
        )
        return trips_pb2.SearchTripsResponse(
            results=self._transformer.to_results(result),
        )

    async def find_round_trip(
        self,
        trip_request: trips_pb2.SearchTripsRequest.RoundTrip,
        passengers: Iterable[trips_pb2.SearchTripsRequest.Passenger],
    ) -> trips_pb2.SearchTripsResponse:
        result: Sequence[quote.Quote] = await self._client.quotes.get_quotes(
            request=self.round_trip_to_offer_request(trip_request, passengers),
        )
        return trips_pb2.SearchTripsResponse(
            results=self._transformer.to_results(result),
        )

    def round_trip_to_offer_request(
        self,
        trip_request: trips_pb2.SearchTripsRequest.RoundTrip,
        passengers: Iterable[trips_pb2.SearchTripsRequest.Passenger],
    ) -> request.QuoteRequest:
        origins, destinations = self._get_ports(trip_request.criterion)
        leg_passengers = self._get_leg_passengers(passengers)
        departure_date_time = _datetime_to_utc_without_tz(
            date_time=datetime.datetime(  # noqa: DTZ001
                year=trip_request.criterion.departure_date.year,
                day=trip_request.criterion.departure_date.day,
                month=trip_request.criterion.departure_date.month,
            ),
        )
        return_date_time = _datetime_to_utc_without_tz(
            date_time=datetime.datetime(  # noqa: DTZ001
                year=trip_request.return_date.year,
                day=trip_request.return_date.day,
                month=trip_request.return_date.month,
            ),
        )
        legs: list[leg.LegBase] = []
        for origin in origins:
            for destination in destinations:
                legs.extend(
                    (
                        leg.LegBase(
                            is_return_leg=False,
                            route_id=self._route.get_by_origin_destination(
                                origin=origin.identifier,
                                destination=destination.identifier,
                            ).route_id,
                            departure_date_time=departure_date_time,
                            passengers=leg_passengers,
                        ),
                        leg.LegBase(
                            is_return_leg=True,
                            route_id=self._route.get_by_origin_destination(
                                origin=destination.identifier,
                                destination=origin.identifier,
                            ).route_id,
                            departure_date_time=return_date_time,
                            passengers=leg_passengers,
                        ),
                    ),
                )
        quote_base = quote.QuoteBase(
            selected_currency=_CURRENCY,
            is_different_outbound_return=True,
            return_alternative_routes=False,
            is_open_ticket=False,
            legs=legs,
        )
        return request.QuoteRequest(quote=quote_base)

    def one_way_to_offer_request(
        self,
        trip_request: trips_pb2.SearchTripsRequest.OneWay,
        passengers: Iterable[trips_pb2.SearchTripsRequest.Passenger],
    ) -> request.QuoteRequest:
        origins, destinations = self._get_ports(trip_request.criterion)
        leg_passengers = self._get_leg_passengers(passengers)
        departure_date_time = _datetime_to_utc_without_tz(
            date_time=datetime.datetime(  # noqa: DTZ001
                year=trip_request.criterion.departure_date.year,
                day=trip_request.criterion.departure_date.day,
                month=trip_request.criterion.departure_date.month,
            ),
        )
        legs: list[leg.LegBase] = [
            leg.LegBase(
                is_return_leg=False,
                route_id=self._route.get_by_origin_destination(
                    origin=origin.identifier,
                    destination=destination.identifier,
                ).route_id,
                departure_date_time=departure_date_time,
                passengers=leg_passengers,
            )
            for origin in origins
            for destination in destinations
        ]
        quote_base = quote.QuoteBase(
            selected_currency=_CURRENCY,
            is_different_outbound_return=True,
            return_alternative_routes=False,
            is_open_ticket=False,
            legs=legs,
        )
        return request.QuoteRequest(quote=quote_base)

    def _get_leg_passengers(
        self,
        passengers: Iterable[trips_pb2.SearchTripsRequest.Passenger],
    ) -> list[passenger.PassengerBase]:
        passengers_ages = [
            date_to_age(
                protobuf.protobuf_to_date(
                    tip_passenger.date_of_birth,
                ),
            )
            for tip_passenger in passengers
        ]
        return [
            passenger.PassengerBase(
                age_range=passenger.AgeRange.parse_raw(
                    json.dumps(
                        {
                            "from": pax_age,
                            "to": pax_age,
                        },
                    ),
                ),
                is_wheelchair_user=False,
                is_lead_passenger=pax_num == 0,
            )
            for pax_num, pax_age in enumerate(
                passengers_ages,
            )
        ]

    def _get_ports(
        self,
        criterion: trips_pb2.SearchTripsRequest.Criterion,
    ) -> tuple[set[port.Port], set[port.Port]]:
        return (
            self._h3_port_mapping.find_mapped_values(
                latlng_pb2.LatLng(
                    latitude=criterion.origin_coordinates.latitude,
                    longitude=criterion.origin_coordinates.longitude,
                ),
            ),
            self._h3_port_mapping.find_mapped_values(
                latlng_pb2.LatLng(
                    latitude=criterion.destination_coordinates.latitude,
                    longitude=criterion.destination_coordinates.longitude,
                ),
            ),
        )


def calculate_result_hash(result: trips_pb2.Result) -> int:
    return hash(result.SerializeToString(deterministic=True))
