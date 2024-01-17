import zoneinfo
from collections.abc import Iterable
from typing import NamedTuple

from snowfall.project.junction.content.service.duffel import parsers
from snowfall.project.junction.provider.v2alpha import trips_pb2
from snowfall.project.junction.v1 import fare_type_pb2, segment_type_pb2
from snowfall.stdlib import time
from snowfall.stdlib.format import protobuf
from snowfall.stdlib.v1 import latlng_pb2
from snowfall.vendor.duffel import client
from snowfall.vendor.duffel.builders import offer_request as request
from snowfall.vendor.duffel.models import common, offer_request, offer_slice


class MissingIataError(Exception):
    """Raised when an airport is missing an IATA."""


class CabinClass(NamedTuple):
    cabin_type: fare_type_pb2.FareType.ValueType
    marketing_name: str


class Transformer(object):
    def to_results(
        self,
        offer_result: offer_request.OfferRequest,
    ) -> list[trips_pb2.Result]:
        results = {}

        for offer in offer_result.offers:
            result = trips_pb2.Result(
                trips=[self.trip_to_proto(trip) for trip in offer.slices],
                base_amount=parsers.amount_to_proto(
                    offer.base_amount,
                    offer.base_currency,
                ),
                tax_amount=parsers.amount_to_proto(
                    offer.tax_amount,
                    offer.tax_currency or offer.total_currency,
                ),
                total_amount=parsers.amount_to_proto(
                    offer.total_amount,
                    offer.total_currency,
                ),
            )
            results[calculate_result_hash(result)] = result

        return list(results.values())

    def trip_to_proto(self, trip: offer_slice.OfferSlice) -> trips_pb2.Trip:
        highest_cabin_class = self._get_highest_cabin_class(trip.segments)

        return trips_pb2.Trip(
            segments=[self.segment_to_proto(segment) for segment in trip.segments],
            fare=trips_pb2.Trip.Fare(
                type=highest_cabin_class.cabin_type,
                marketing_name=trip.fare_brand_name
                or highest_cabin_class.marketing_name,
            ),
        )

    def segment_to_proto(
        self,
        segment: offer_slice.OfferSliceSegment,
    ) -> trips_pb2.Segment:
        departure_at = segment.departing_at.replace(
            tzinfo=zoneinfo.ZoneInfo(segment.origin.time_zone),
        )
        arrival_at = segment.arriving_at.replace(
            tzinfo=zoneinfo.ZoneInfo(segment.destination.time_zone),
        )

        return trips_pb2.Segment(
            origin=self._location_to_proto(segment.origin),
            destination=self._location_to_proto(segment.destination),
            departure_at=protobuf.datetime_to_protobuf_datetime(departure_at),
            arrival_at=protobuf.datetime_to_protobuf_datetime(arrival_at),
            stops=self._stops_to_proto(segment),
            type=segment_type_pb2.SEGMENT_TYPE_FLIGHT,
            marketed_by=trips_pb2.Segment.Company(
                route_number=segment.marketing_carrier_flight_number,
                code=segment.marketing_carrier.iata_code or "",
                name=segment.marketing_carrier.name,
            ),
            operated_by=trips_pb2.Segment.Company(
                route_number=segment.operating_carrier_flight_number or "",
                code=segment.operating_carrier.iata_code or "",
                name=segment.operating_carrier.name,
            ),
            vehicle=self._aircraft_to_proto(segment),
            passengers=[
                self._passenger_to_proto(passenger) for passenger in segment.passengers
            ],
        )

    def _stops_to_proto(
        self,
        segment: offer_slice.OfferSliceSegment,
    ) -> list[trips_pb2.Stop]:
        return [self._stop_to_proto(stop) for stop in segment.stops]

    def _stop_to_proto(self, stop: offer_slice.Stop) -> trips_pb2.Stop:
        zone_info = zoneinfo.ZoneInfo(stop.airport.time_zone)
        departure_at = stop.departing_at.replace(tzinfo=zone_info)
        arrival_at = stop.arriving_at.replace(tzinfo=zone_info)

        return trips_pb2.Stop(
            arrival_at=protobuf.datetime_to_protobuf_datetime(arrival_at),
            departure_at=protobuf.datetime_to_protobuf_datetime(departure_at),
            location=self._location_to_proto(stop.airport),
        )

    def _location_to_proto(self, location: common.Airport) -> trips_pb2.Location:
        if not location.iata_code:
            raise MissingIataError(
                "{name} ({identifier}) is missing an IATA code.".format(
                    name=location.name,
                    identifier=location.identifier,
                ),
            )
        return trips_pb2.Location(
            ref=location.iata_code,
            name=location.name,
            coordinates=latlng_pb2.LatLng(
                longitude=location.longitude,
                latitude=location.latitude,
            ),
        )

    def _get_highest_cabin_class(
        self,
        segments: Iterable[offer_slice.OfferSliceSegment],
    ) -> CabinClass:
        passenger_with_highest_cabin = max(
            (passenger for segment in segments for passenger in segment.passengers),
            key=self._resolve_passenger_cabin_class,
        )

        return CabinClass(
            cabin_type=self._resolve_passenger_cabin_class(
                passenger_with_highest_cabin,
            ),
            marketing_name=passenger_with_highest_cabin.cabin_class_marketing_name,
        )

    def _resolve_passenger_cabin_class(
        self,
        passenger: offer_slice.OfferSliceSegmentPassenger,
    ) -> fare_type_pb2.FareType.ValueType:
        match passenger.cabin_class:
            case "first":
                return fare_type_pb2.FARE_TYPE_FIRST
            case "business":
                return fare_type_pb2.FARE_TYPE_BUSINESS
            case "economy" | "premium_economy":
                return fare_type_pb2.FARE_TYPE_ECONOMY

        return fare_type_pb2.FARE_TYPE_UNSPECIFIED

    def _aircraft_to_proto(
        self,
        segment: offer_slice.OfferSliceSegment,
    ) -> trips_pb2.Segment.Vehicle | None:
        if not segment.aircraft:
            return None

        return trips_pb2.Segment.Vehicle(
            code=segment.aircraft.iata_code,
            name=segment.aircraft.name,
        )

    def _passenger_to_proto(
        self,
        passenger: offer_slice.OfferSliceSegmentPassenger,
    ) -> trips_pb2.Segment.Passenger:
        return trips_pb2.Segment.Passenger(
            seating=trips_pb2.Segment.Passenger.Seating(
                type=self._resolve_passenger_cabin_class(passenger),
                marketing_name=passenger.cabin_class_marketing_name,
            ),
        )


class Trips(object):
    def __init__(self, search_client: client.DuffelClient, transformer: Transformer):
        self._client = search_client
        self._transformer = transformer

    async def find_one_way(
        self,
        trip_request: trips_pb2.SearchTripsRequest.OneWay,
        passengers: Iterable[trips_pb2.SearchTripsRequest.Passenger],
    ) -> trips_pb2.SearchTripsResponse:
        result = await self._client.create_offer_request(
            offer_request_data=one_way_to_offer_request(trip_request, passengers),
        )

        return trips_pb2.SearchTripsResponse(
            results=self._transformer.to_results(result),
        )


def one_way_to_offer_request(
    trip_request: trips_pb2.SearchTripsRequest.OneWay,
    passengers: Iterable[trips_pb2.SearchTripsRequest.Passenger],
) -> request.OfferRequestData:
    criterion = trip_request.criterion

    return request.OfferRequestData(
        offer_data=request.OfferRequestDataList(
            passengers=[
                request.OfferRequestPassenger(
                    age=time.date_to_age(
                        date_of_birth=protobuf.protobuf_to_date(
                            passenger.date_of_birth,
                        ),
                        at_date=protobuf.protobuf_to_date(criterion.departure_date),
                    ),
                )
                for passenger in passengers
            ],
            slices=[
                request.OfferRequestSlice(
                    origin=criterion.origin_identifier,
                    destination=criterion.destination_identifier,
                    departure_date=protobuf.protobuf_to_date(criterion.departure_date),
                ),
            ],
        ),
    )


def calculate_result_hash(result: trips_pb2.Result) -> int:
    return hash(result.SerializeToString(deterministic=True))


def is_duplicate_trip(first: trips_pb2.Trip, second: trips_pb2.Trip) -> bool:
    return first.SerializeToString(deterministic=True) == second.SerializeToString(
        deterministic=True,
    )
