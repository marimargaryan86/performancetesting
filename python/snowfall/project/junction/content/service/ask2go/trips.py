import asyncio
import zoneinfo
from collections.abc import AsyncIterator, Iterable
from types import MappingProxyType
from typing import cast

from snowfall.project.junction.go.v1.models_pb2 import CabinClass
from snowfall.project.junction.provider import airports, cabin_classes
from snowfall.project.junction.provider.v2alpha import trips_pb2
from snowfall.project.junction.v1 import fare_type_pb2, segment_type_pb2
from snowfall.stdlib import money, time
from snowfall.stdlib.format import protobuf
from snowfall.stdlib.v1 import latlng_pb2, money_pb2
from snowfall.vendor.ask2go.adapter import Adapter
from snowfall.vendor.ask2go.models import offers
from snowfall.vendor.ask2go.models import search as search_model

_AdultMinAge = 18
_InfantMaxAge = 2

CABIN_TO_FARE_MAPPING = MappingProxyType({
    CabinClass.TYPE_UNSPECIFIED: fare_type_pb2.FARE_TYPE_UNSPECIFIED,
    CabinClass.TYPE_ECONOMY: fare_type_pb2.FARE_TYPE_ECONOMY,
    CabinClass.TYPE_PREMIUM: fare_type_pb2.FARE_TYPE_BUSINESS,
    CabinClass.TYPE_BUSINESS: fare_type_pb2.FARE_TYPE_BUSINESS,
    CabinClass.TYPE_FIRST: fare_type_pb2.FARE_TYPE_FIRST,
})


class MissingIataError(Exception):
    """Raised when an airport is missing an IATA."""


class Transformer(object):
    def __init__(
        self,
        airport_repository: airports.AirportRepository,
        cabin_mapping_repository: cabin_classes.CabinMappingRepository,
    ):
        self._airports = airport_repository
        self._cabin_mappings = cabin_mapping_repository

    async def to_results(
        self,
        offer_results: AsyncIterator[offers.Offer],
    ) -> list[trips_pb2.Result]:
        results = []
        async for offer in offer_results:
            prices = (
                offer.pricing_information.base,
                *offer.pricing_information.additional,
            )
            for pr in prices:
                res = trips_pb2.Result(
                    trips=await asyncio.gather(
                        *(
                            self.trip_to_proto(tr, pr.brand_name or "")
                            for tr in offer.trips
                        ),
                    ),
                    base_amount=self._amount_to_proto(pr.base_fare, pr.currency),
                    tax_amount=self._amount_to_proto(pr.total_tax, pr.currency),
                    total_amount=self._amount_to_proto(pr.total_cost, pr.currency),
                )
                results.append(res)
        return results

    async def trip_to_proto(self, trip: offers.Trip, fare_brand: str) -> trips_pb2.Trip:
        cabin_type = await self._cabin_mappings.resolve_cabin_class(
            fare_brand=fare_brand,
            operator=str(trip.segments[0].operating_carrier.code),
        )
        fare_type = CABIN_TO_FARE_MAPPING.get(
            cabin_type,
            fare_type_pb2.FARE_TYPE_UNSPECIFIED,
        )
        return trips_pb2.Trip(
            segments=[self.segment_to_proto(segment) for segment in trip.segments],
            fare=trips_pb2.Trip.Fare(
                type=fare_type,
                marketing_name=trip.segments[0].cabin or "",
            ),
        )

    def segment_to_proto(
        self,
        segment: offers.TripSegment,
    ) -> trips_pb2.Segment:
        origin, origin_tz = self._location_to_proto(
            cast(offers.TripOriginDestinationFlight, segment.origin).airport_code,
        )
        dest, dest_tz = self._location_to_proto(
            cast(offers.TripOriginDestinationFlight, segment.destination).airport_code,
        )
        departure_at = segment.departure.date_time.replace(
            tzinfo=zoneinfo.ZoneInfo(origin_tz),
        )
        arrival_at = segment.arrival.date_time.replace(
            tzinfo=zoneinfo.ZoneInfo(dest_tz),
        )
        return trips_pb2.Segment(
            origin=origin,
            destination=dest,
            departure_at=protobuf.datetime_to_protobuf_datetime(departure_at),
            arrival_at=protobuf.datetime_to_protobuf_datetime(arrival_at),
            type=segment_type_pb2.SEGMENT_TYPE_FLIGHT,
            marketed_by=trips_pb2.Segment.Company(code=segment.marketing_carrier.code),
            operated_by=trips_pb2.Segment.Company(code=segment.operating_carrier.code),
            vehicle=trips_pb2.Segment.Vehicle(
                code=segment.aircraft.flight_number,
                name=segment.aircraft.equipment,
            ),
        )

    def _location_to_proto(self, iata: str) -> tuple[trips_pb2.Location, str]:
        location = self._airports.get_by_iata(iata)
        return trips_pb2.Location(
            ref=location.identifier,
            name=location.airport_name or "",
            coordinates=latlng_pb2.LatLng(
                longitude=location.longitude,
                latitude=location.latitude,
            ),
        ), location.timezone.key

    def _amount_to_proto(
        self,
        amount: str | None,
        currency: str,
    ) -> money_pb2.Money:
        if not amount:
            return money.Money(0, money.Currency(currency)).protobuf()

        return money.from_string(amount, money.Currency(currency)).protobuf()


class Trips(object):
    def __init__(self, adapter: Adapter, transformer: Transformer):
        self._adapter = adapter
        self._transformer = transformer

    async def find_one_way(
        self,
        trip_request: trips_pb2.SearchTripsRequest.OneWay,
        passengers: Iterable[trips_pb2.SearchTripsRequest.Passenger],
    ) -> trips_pb2.SearchTripsResponse:
        criterion = trip_request.criterion
        adults = 0
        children = 0
        infants = 0
        for passenger in passengers:
            age = time.date_to_age(
                date_of_birth=protobuf.protobuf_to_date(passenger.date_of_birth),
                at_date=protobuf.protobuf_to_date(criterion.departure_date),
            )
            if age >= _AdultMinAge:
                adults += 1
            elif age > _InfantMaxAge:
                children += 1
            else:
                infants += 1

        search_criteria = search_model.CreateSearchCriteria(
            origin_iata=criterion.origin_identifier,
            destination_iata=criterion.destination_identifier,
            outbound_date=protobuf.protobuf_to_date(criterion.departure_date),
            adults=adults,
            children=children,
            infants=infants,
        )
        results = self._adapter.gather_search_results(search_criteria)
        return trips_pb2.SearchTripsResponse(
            results=await self._transformer.to_results(results),
        )


def calculate_result_hash(result: trips_pb2.Result) -> int:
    return hash(result.SerializeToString(deterministic=True))


def is_duplicate_trip(first: trips_pb2.Trip, second: trips_pb2.Trip) -> bool:
    return first.SerializeToString(deterministic=True) == second.SerializeToString(
        deterministic=True,
    )
