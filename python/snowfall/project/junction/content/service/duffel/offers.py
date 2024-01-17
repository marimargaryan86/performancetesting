from collections.abc import Iterable

from snowfall.project.junction.content.service.duffel import parsers
from snowfall.project.junction.provider.v2alpha import trips_pb2
from snowfall.stdlib import time
from snowfall.stdlib.format import protobuf
from snowfall.vendor.duffel import client
from snowfall.vendor.duffel.builders import offer_request as request_builder
from snowfall.vendor.duffel.models import offer_request as offer_response

_TIME_FORMAT = "%H:%M"


class Transformer(object):
    def to_results(
        self,
        offer_result: offer_response.OfferRequest,
    ) -> list[trips_pb2.Offer]:
        return [
            trips_pb2.Offer(
                id=offer.identifier,
                expires_at=protobuf.datetime_to_protobuf(offer.expires_at),
                price=trips_pb2.Price(
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
                ),
            )
            for offer in offer_result.offers
        ]


class Offers(object):
    def __init__(self, search_client: client.DuffelClient, transformer: Transformer):
        self._client = search_client
        self._transformer = transformer

    async def find_one_way(
        self,
        offer_request: trips_pb2.SearchOffersRequest.OneWay,
        passengers: Iterable[trips_pb2.SearchOffersRequest.Passenger],
    ) -> trips_pb2.SearchOffersResponse:
        result = await self._client.create_offer_request(
            offer_request_data=one_way_to_offer_request(offer_request, passengers),
        )

        return trips_pb2.SearchOffersResponse(
            offers=self._transformer.to_results(result),
        )


def one_way_to_offer_request(
    trip_request: trips_pb2.SearchOffersRequest.OneWay,
    passengers: Iterable[trips_pb2.SearchOffersRequest.Passenger],
) -> request_builder.OfferRequestData:
    # TODO(bolmis): handle multiple segments
    segment = trip_request.trip.segments[0]
    departure_time = protobuf.protobuf_to_datetime(segment.departure_at).strftime(
        _TIME_FORMAT,
    )
    arrival_time = protobuf.protobuf_to_datetime(segment.arrival_at).strftime(
        _TIME_FORMAT,
    )

    return request_builder.OfferRequestData(
        offer_data=request_builder.OfferRequestDataList(
            passengers=[
                request_builder.OfferRequestPassenger(
                    age=time.date_to_age(
                        date_of_birth=protobuf.protobuf_to_date(
                            passenger.date_of_birth,
                        ),
                        at_date=protobuf.protobuf_to_date(segment.departure_at),
                    ),
                )
                for passenger in passengers
            ],
            slices=[
                request_builder.OfferRequestSlice(
                    origin=segment.origin_ref,
                    destination=segment.destination_ref,
                    departure_date=protobuf.protobuf_to_date(segment.departure_at),
                    departure_time=request_builder.OfferRequestSliceTimeRange(
                        time_from=departure_time,
                        to=departure_time,
                    ),
                    arrival_time=request_builder.OfferRequestSliceTimeRange(
                        time_from=arrival_time,
                        to=arrival_time,
                    ),
                ),
            ],
        ),
    )
