from collections.abc import Sequence

from snowfall.project.junction.content.service.mock import client
from snowfall.project.junction.provider.v2alpha import trips_pb2
from snowfall.project.junction.v1 import segment_type_pb2
from snowfall.stdlib.format import protobuf
from snowfall.stdlib.v1 import latlng_pb2, money_pb2


class Transformer(object):
    def to_proto(
        self,
        search_results: Sequence[client.SearchResult],
    ) -> trips_pb2.SearchTripsResponse:
        return trips_pb2.SearchTripsResponse(
            results=[
                self._make_result(search_result, fare)
                for search_result in search_results
                for fare in search_result.fares
            ],
        )

    def _make_result(
        self,
        search_result: client.SearchResult,
        fare: client.Fare,
    ) -> trips_pb2.Result:
        price = fare.price.protobuf()
        return trips_pb2.Result(
            trips=[
                trips_pb2.Trip(
                    segments=[
                        _make_segment(segment=segment) for segment in trip.segments
                    ],
                    fare=trips_pb2.Trip.Fare(
                        type=fare.brand_type,
                        marketing_name=fare.brand_name,
                    ),
                )
                for trip in search_result.trips
            ],
            base_amount=price,
            tax_amount=money_pb2.Money(currency_code=price.currency_code),
            total_amount=price,
        )


class Trips(object):
    def __init__(self, search_client: client.MockClient, transformer: Transformer):
        self._client = search_client
        self._transformer = transformer

    async def find(
        self,
        trip_request: trips_pb2.SearchTripsRequest,
    ) -> trips_pb2.SearchTripsResponse:
        match trip_request.WhichOneof("search_mode"):
            case "one_way":
                return self._transformer.to_proto(
                    self._client.find_one_way(trip_request.one_way),
                )
            case "round_trip":
                return self._transformer.to_proto(
                    self._client.find_round_trip(trip_request.round_trip),
                )
            case "multi_city":
                return self._transformer.to_proto(
                    self._client.find_multi_city(trip_request.multi_city),
                )

        return trips_pb2.SearchTripsResponse()


def _make_segment(
    segment: client.Segment,
) -> trips_pb2.Segment:
    return trips_pb2.Segment(
        origin=trips_pb2.Location(
            ref=segment.origin.identifier,
            name=segment.origin.name,
            coordinates=latlng_pb2.LatLng(
                latitude=segment.origin.latitude,
                longitude=segment.origin.longitude,
            ),
        ),
        destination=trips_pb2.Location(
            ref=segment.destination.identifier,
            name=segment.destination.name,
            coordinates=latlng_pb2.LatLng(
                latitude=segment.destination.latitude,
                longitude=segment.destination.longitude,
            ),
        ),
        departure_at=protobuf.datetime_to_protobuf_datetime(
            segment.departure_at,
        ),
        arrival_at=protobuf.datetime_to_protobuf_datetime(segment.arrival_at),
        type=segment_type_pb2.SEGMENT_TYPE_FLIGHT,
        marketed_by=trips_pb2.Segment.Company(
            route_number=segment.marketed_by.flight_number,
            code=segment.marketed_by.code,
            name=segment.marketed_by.name,
        ),
        operated_by=trips_pb2.Segment.Company(
            route_number=segment.operated_by.flight_number,
            code=segment.operated_by.code,
            name=segment.operated_by.name,
        ),
    )
