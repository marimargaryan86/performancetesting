from collections.abc import Iterable
from typing import NamedTuple

from snowfall.project.junction.content.service.duffel import parsers
from snowfall.project.junction.provider.v2alpha import trips_pb2
from snowfall.project.junction.v1 import fare_type_pb2
from snowfall.stdlib import time
from snowfall.stdlib.format import protobuf
from snowfall.vendor.duffel import client
from snowfall.vendor.duffel.builders import offer_request as request
from snowfall.vendor.duffel.models import offer_request


class MissingIataError(Exception):
    """Raised when an airport is missing an IATA."""


class CabinClass(NamedTuple):
    cabin_type: fare_type_pb2.FareType.ValueType
    marketing_name: str


class Transformer(object):
    def __init__(self, trip_parser: parsers.TripParser):
        self._trip_parser = trip_parser

    def to_results(
        self,
        offer_result: offer_request.OfferRequest,
    ) -> list[trips_pb2.Result]:
        results = {}

        for offer in offer_result.offers:
            result = trips_pb2.Result(
                trips=[self._trip_parser.trip_to_proto(trip) for trip in offer.slices],
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
