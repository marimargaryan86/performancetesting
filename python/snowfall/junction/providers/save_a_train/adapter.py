import datetime
import uuid
from typing import AsyncIterator

import more_itertools

from snowfall.common.v1alpha import models_pb2
from snowfall.junction.providers.save_a_train import train_stations
from snowfall.junction.providers.save_a_train.v1alpha import amqp_pb2
from snowfall.junction.providers.v1alpha import offers_pb2
from snowfall.stdlib.format import protobuf
from snowfall.vendor.sat import client
from snowfall.vendor.sat.enums import TripType
from snowfall.vendor.sat.exceptions import SATValidationError
from snowfall.vendor.sat.models import general_search, request


class NoResultsError(Exception):
    """Raised when a result page has not results."""


class SaveATrainAdapter(object):
    _poll_retries_limit = 10
    _wait_time_between_polling = 1

    def __init__(
        self,
        save_a_train_client: client.SATClient,
        train_station_repository: train_stations.TrainStationRepository,
        ttl: datetime.timedelta,
    ):
        self._train_stations = train_station_repository
        self._client = save_a_train_client
        self._ttl = ttl

    async def gather_search_results(
        self,
        search_task: amqp_pb2.SearchCriteriaTask,
    ) -> AsyncIterator[offers_pb2.GroupedOffer]:
        origin = self._train_stations.get_by_id(search_task.criteria.origin_id)
        destination = self._train_stations.get_by_id(
            search_task.criteria.destination_id,
        )
        try:
            search_response = await self._client.get_general_search_results(
                request.GeneralSearchResultsRequest(
                    origin_id=origin.id,
                    destination_id=destination.id,
                    trip_type=TripType.one_way,
                    number_of_passengers=search_task.criteria.number_of_passengers,
                    departure_date=datetime.date(
                        year=search_task.criteria.departure_date.year,
                        month=search_task.criteria.departure_date.month,
                        day=search_task.criteria.departure_date.day,
                    ),
                ),
            )
        except SATValidationError as error:
            raise NoResultsError(error)

        list_of_offers = search_response.general_search_result.outbound

        for offer in list_of_offers:
            if offer_matches_requirements(offer):
                yield offers_pb2.GroupedOffer(
                    id=str(uuid.uuid4()),  # todo: persist so it can be booked
                    offer_search_id=search_task.offer_search_id,
                    expires_at=protobuf.datetime_to_protobuf(
                        datetime.datetime.now(tz=datetime.timezone.utc) + self._ttl,
                    ),
                    offers=[
                        offers_pb2.Offer(
                            id=str(uuid.uuid4()),  # todo: persist so it can be booked
                            segments=[
                                offers_pb2.OfferSegment(
                                    id=search_task.segments[0].id,
                                ),
                            ],
                            price=models_pb2.Price(
                                amount=int(
                                    min(offer.price.values())
                                    * 100,  # TODO: add cabin fare
                                ),
                                currency="USD",  # TODO: read currency from settings
                            ),
                        ),
                    ],
                    segments=[
                        offers_pb2.Segment(
                            id=search_task.segments[0].id,
                            vehicle=offers_pb2.Vehicle(
                                equipment="train",  # TODO: add something useful
                                number=offer.train_numbers,
                            ),
                            operator=offer.operator,
                            vendor=offer.operator,
                            terminal="foobar",  # TODO: add something useful
                            legs=[
                                offers_pb2.Leg(
                                    id=more_itertools.first(
                                        more_itertools.first(search_task.segments).legs,
                                    ).id,
                                    origin=models_pb2.Point(
                                        ref=origin.id,
                                        name=str(origin.name),
                                        coordinates=models_pb2.Coordinates(
                                            latitude=origin.latitude,
                                            longitude=origin.longitude,
                                        ),
                                        time_zone=origin.timezone.key,
                                    ),
                                    destination=models_pb2.Point(
                                        ref=destination.id,
                                        name=str(destination.name),
                                        coordinates=models_pb2.Coordinates(
                                            latitude=destination.latitude,
                                            longitude=destination.longitude,
                                        ),
                                        time_zone=destination.timezone.key,
                                    ),  # TODO: add departure and arrival dates
                                ),
                            ],
                        ),
                    ],
                )


def offer_matches_requirements(offer: general_search.GeneralTrip) -> bool:
    return True  # TODO: check departure and arrival datetime for a match
