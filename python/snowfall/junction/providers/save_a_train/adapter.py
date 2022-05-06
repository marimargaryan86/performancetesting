from __future__ import annotations

import datetime
import types
import uuid
from typing import AsyncIterator

import httpx
import more_itertools
import phonenumbers
import pycountry
import structlog

from snowfall.common.v1alpha import models_pb2
from snowfall.junction.offers.v1alpha import models_pb2 as offer_models_pb2
from snowfall.junction.orders.v1alpha import models_pb2 as order_models_pb2
from snowfall.junction.providers.save_a_train import cache, models, train_stations
from snowfall.junction.providers.save_a_train.v1alpha import amqp_pb2
from snowfall.stdlib.format import protobuf
from snowfall.vendor.sat import client, enums, exceptions
from snowfall.vendor.sat import models as sat_models

_CABIN_MAPPING = types.MappingProxyType(
    {
        "second_class": models_pb2.CabinClass.TYPE_ECONOMY,
        "first_class": models_pb2.CabinClass.TYPE_BUSINESS,
        "business_class": models_pb2.CabinClass.TYPE_FIRST,
    },
)


class SaveATrainAdapterError(Exception):
    """Raised when there is an exception in the Save a Train adapter."""


class NoResultsError(SaveATrainAdapterError):
    """Raised when a result page has not results."""


class BookingError(SaveATrainAdapterError):
    """Raised when a booking error is encountered."""


class SaveATrainAdapter(object):
    _poll_retries_limit = 10
    _wait_time_between_polling = 1

    def __init__(
        self,
        save_a_train_client: client.SATClient,
        train_station_repository: train_stations.TrainStationRepository,
        offers_cache: cache.OffersCache,
        ttl: datetime.timedelta,
    ) -> None:
        self._train_stations = train_station_repository
        self._client = save_a_train_client
        self._offers_cache = offers_cache
        self._ttl = ttl
        self._logger = structlog.get_logger(__name__)

    async def gather_search_results(  # noqa: C901,WPS210,WPS231
        self,
        search_task: amqp_pb2.SearchCriteriaTask,
    ) -> AsyncIterator[offer_models_pb2.OfferGroup]:
        origin = self._train_stations.get_by_id(search_task.criteria.origin_id)
        destination = self._train_stations.get_by_id(
            search_task.criteria.destination_id,
        )

        try:
            general_search_response = await self._client.get_general_search_results(
                sat_models.request.GeneralSearchResultsRequest(
                    origin_id=origin.id,
                    destination_id=destination.id,
                    trip_type=enums.TripType.one_way,
                    number_of_passengers=len(search_task.criteria.passengers_ages),
                    departure_date=protobuf.protobuf_to_date(
                        search_task.criteria.departure_datetime,
                    ),
                ),
            )
        except httpx.TimeoutException as timeout_error:
            self._logger.info("SAT timeout error occurred.", error=timeout_error)
        else:
            requirement = models.GeneralSearchResultRequirement(
                departure_datetime=protobuf.protobuf_to_datetime(
                    search_task.criteria.departure_datetime,
                ),
                arrival_datetime=protobuf.protobuf_to_datetime(
                    search_task.criteria.arrival_datetime,
                ),
            )
            result_matches = any(
                self._general_search_result_matches_requirement(trip, requirement)
                for trip in general_search_response.general_search_result.outbound
            )
            if not result_matches:
                raise NoResultsError("No results matching search criteria")

        try:
            search_response = await self._client.create_search(
                sat_models.request.CreateSearchRequest(
                    origin_id=origin.id,
                    destination_id=destination.id,
                    passengers_ages=list(search_task.criteria.passengers_ages),
                    departure_datetime=protobuf.protobuf_to_datetime(
                        search_task.criteria.departure_datetime,
                    ),
                ),
            )
        except exceptions.SATValidationError as search_error:
            raise NoResultsError(search_error)
        except httpx.HTTPStatusError as http_error:
            if http_error.response.text:
                raise_http_error_with_text(http_error)
            raise http_error

        for search_result in search_response.search_results:
            if self._search_result_matches_requirements(search_result):
                try:
                    search_details = await self._client.get_search_result_details(
                        sat_models.request.SearchResultRequest(
                            search_id=search_response.identifier,
                            search_result_id=search_result.identifier,
                        ),
                    )
                except exceptions.SATValidationError:
                    continue
                except httpx.HTTPStatusError:
                    continue

                yield offer_models_pb2.OfferGroup(
                    id=str(uuid.uuid4()),
                    offer_search_id=search_task.offer_search_id,
                    expires_at=protobuf.datetime_to_protobuf(
                        datetime.datetime.now(tz=datetime.timezone.utc) + self._ttl,
                    ),
                    offers=[
                        offer_models_pb2.Offer(
                            id=await self._offers_cache.store(
                                search_id=search_response.identifier,
                                search_result_id=search_result.identifier,
                                transfer_id=transfer.identifier,
                                fare_id=transfer_fare.identifier,
                            ),
                            segment_details=[
                                offer_models_pb2.OfferSegmentDetails(
                                    id=search_task.segments[0].id,
                                    cabin_class=models_pb2.CabinClass(
                                        type=_cabin_to_proto(transfer_fare.name),
                                        marketing_name=transfer_fare.name.replace(
                                            "_",
                                            " ",
                                        ).capitalize(),
                                    ),
                                ),
                            ],
                            price=models_pb2.Price(
                                amount=int(
                                    transfer_fare.price * 100,
                                ),
                                currency="EUR",
                            ),
                        )
                        for transfer in search_details.transfers
                        for transfer_fare in transfer.fares
                    ],
                    segments=[
                        offer_models_pb2.OfferSegment(
                            id=search_task.segments[0].id,
                            vehicle=offer_models_pb2.Vehicle(
                                equipment=transfer_change.train.category or "",
                                number=transfer_change.train.number or "",
                            ),
                            operator="foobar",  # TODO: add something useful
                            vendor="foobar",  # TODO: add something useful
                            terminal="foobar",  # TODO: add something useful
                            legs=[
                                offer_models_pb2.OfferSegmentLeg(
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
                                    ),
                                    departure_at=protobuf.datetime_to_protobuf(
                                        search_result.departure_datetime.replace(
                                            tzinfo=origin.timezone,
                                        ),
                                    ),
                                    arrival_at=protobuf.datetime_to_protobuf(
                                        search_result.arrival_datetime.replace(
                                            tzinfo=destination.timezone,
                                        ),
                                    ),
                                ),
                            ],
                        )
                        for transfer in search_details.transfers
                        for transfer_change in transfer.changes
                        if transfer_change.transport_type == "train"
                    ],
                )

    async def create_booking(
        self,
        offer_id: str,
        order: order_models_pb2.Order,
    ) -> str:
        select_search_result = await self._select_search_result(offer_id, order)

        passenger = order.passengers[0]  # TODO: handle multiple passengers
        title_map = {  # TODO: map unspecified to something else?
            order_models_pb2.Passenger.Title.TITLE_UNSPECIFIED: enums.PassengerTitle.mr,
            order_models_pb2.Passenger.Title.TITLE_MR: enums.PassengerTitle.mr,
            order_models_pb2.Passenger.Title.TITLE_MRS: enums.PassengerTitle.mrs,
            order_models_pb2.Passenger.Title.TITLE_MISS: enums.PassengerTitle.miss,
            order_models_pb2.Passenger.Title.TITLE_MS: enums.PassengerTitle.ms,
        }

        try:
            booking_result = await self._client.create_booking(
                sat_models.request.CreateBookingRequest(
                    search_id=select_search_result.search_identifier,
                    passengers=[
                        sat_models.booking.Passenger(
                            title=title_map[passenger.title],
                            first_name=passenger.first_name,
                            last_name=passenger.last_name,
                            date_of_birth=protobuf.protobuf_to_date(
                                passenger.date_of_birth,
                            ),
                            gender=(  # TODO: gender unspecified?
                                enums.PassengerGender.male
                                if passenger.gender
                                == order_models_pb2.Passenger.GENDER_MALE
                                else enums.PassengerGender.female
                            ),
                            email=order.contact_details.email,
                            phone_number=str(
                                phonenumbers.parse(
                                    order.contact_details.phone.e164_number,
                                ).national_number,
                            ),
                            country=pycountry.countries.get(
                                alpha_2=order.contact_details.address.region_code,
                            ).name,
                        ),
                    ],
                ),
            )
        except exceptions.SATValidationError as booking_error:
            raise BookingError(booking_error)
        except httpx.HTTPStatusError as http_error:
            if http_error.response.text:
                raise_http_error_with_text(http_error)
            raise http_error

        # TODO: do we need to confirm the booking + get the ticket?
        return booking_result.json()

    async def _select_search_result(
        self,
        offer_id: str,
        order: order_models_pb2.Order,
    ) -> sat_models.search_result_selection.SearchResultSelectionResponse:
        offer_details = await self._offers_cache.fetch(offer_id)

        if not offer_details:
            raise BookingError("No offer with id: '{0}' found.".format(offer_id))

        search_id, search_result_id, transfer_id, fare_id = offer_details

        try:
            return await self._client.select_search_result(
                sat_models.request.SelectSearchResultRequest(
                    search_id=search_id,
                    search_result_id=search_result_id,
                    transfer_id=transfer_id,
                    fare_id=fare_id,
                ),
            )
        except exceptions.SATValidationError as search_error:
            raise BookingError(search_error)
        except httpx.HTTPStatusError as http_error:
            if http_error.response.text:
                raise_http_error_with_text(http_error)
            raise http_error

    def _general_search_result_matches_requirement(
        self,
        general_search_result: sat_models.general_search.GeneralTrip,
        requirement: models.GeneralSearchResultRequirement,
    ) -> bool:
        departure_datetime = datetime.datetime.combine(
            general_search_result.departure_date,
            general_search_result.departure_time,
            tzinfo=requirement.departure_datetime.tzinfo,
        )
        arrival_datetime = datetime.datetime.combine(
            general_search_result.departure_date,
            general_search_result.departure_time,
            tzinfo=requirement.arrival_datetime.tzinfo,
        )
        return (
            departure_datetime == requirement.departure_datetime
            and arrival_datetime == requirement.arrival_datetime
        )

    def _search_result_matches_requirements(
        self,
        search: sat_models.search.SearchResult,
    ) -> bool:
        return True  # TODO: check departure and arrival datetime for a match


def _cabin_to_proto(cabin: str) -> models_pb2.CabinClass.Type.V:
    try:
        return _CABIN_MAPPING[cabin]
    except KeyError:
        return models_pb2.CabinClass.TYPE_UNSPECIFIED


def raise_http_error_with_text(http_error: httpx.HTTPStatusError) -> None:
    raise SaveATrainAdapterError(
        "HTTPStatusError text: {0}".format(
            http_error.response.text,
        ),
    ) from http_error
