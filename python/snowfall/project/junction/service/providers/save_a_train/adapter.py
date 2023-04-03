from __future__ import annotations

import datetime
from typing import AsyncIterator, Sequence

import httpx
import phonenumbers
import pycountry
import structlog

from snowfall.project.junction.go.service.offers.v1alpha import (
    models_pb2 as offer_models_pb2,
)
from snowfall.project.junction.go.service.orders.v1alpha import (
    amqp_pb2 as order_amqp_pb2,
)
from snowfall.project.junction.go.service.orders.v1alpha import (
    models_pb2 as order_models_pb2,
)
from snowfall.project.junction.provider import cabin_classes
from snowfall.project.junction.provider import notifications as base_notifications
from snowfall.project.junction.service.providers.save_a_train import (
    cache,
    models,
    train_stations,
)
from snowfall.project.junction.service.providers.save_a_train.v1alpha import amqp_pb2
from snowfall.stdlib import money, string
from snowfall.stdlib.format import protobuf
from snowfall.stdlib.transport.amqp import producer
from snowfall.stdlib.v1alpha import models_pb2
from snowfall.vendor.save_a_train import client, enums, exceptions
from snowfall.vendor.save_a_train.models import (
    booking,
    request,
    search_result_selection,
)

logger = structlog.get_logger(__name__)


class SaveATrainAdapterError(Exception):
    """Raised when there is an exception in the Save a Train adapter."""


class NoResultsError(SaveATrainAdapterError):
    """Raised when a result page has not results."""


class BookingError(SaveATrainAdapterError):
    """Raised when a booking error is encountered."""


class SaveATrainAdapter(object):  # noqa: WPS214
    _poll_retries_limit = 10
    _wait_time_between_polling = 1

    def __init__(  # noqa: WPS211
        self,
        save_a_train_client: client.SATClient,
        train_station_repository: train_stations.TrainStationRepository,
        offers_cache: cache.OffersCache,
        ttl: datetime.timedelta,
        notifier: base_notifications.Notifier,
        provider_cabin_class_mapping: cabin_classes.CabinMappingRepository,
        notifications_producer: producer.Producer,
    ) -> None:
        self._train_stations = train_station_repository
        self._cabin_mapping = provider_cabin_class_mapping
        self._client = save_a_train_client
        self._offers_cache = offers_cache
        self._ttl = ttl
        self._notifier = notifier
        self._notifications_producer = notifications_producer
        self._logger = structlog.get_logger(__name__)

    def search_criteria_generator(
        self,
        search_task: amqp_pb2.SearchCriteriaTask,
    ) -> request.CreateSearchRequest:
        origin = self._train_stations.get_by_id(
            search_task.criteria.origin_id,
        )
        destination = self._train_stations.get_by_id(
            search_task.criteria.destination_id,
        )
        return request.CreateSearchRequest(
            origin_id=origin.identifier,
            destination_id=destination.identifier,
            passengers_ages=list(search_task.criteria.passengers_ages),
            departure_datetime=protobuf.protobuf_to_datetime(
                search_task.criteria.departure_datetime,
            ),
        )

    def generate_cache_key(self, search_criteria: request.CreateSearchRequest) -> str:
        return string.to_uuid(
            b"\x00".decode().join(
                [
                    search_criteria.origin_id,
                    str(search_criteria.destination_id),
                    str(search_criteria.departure_datetime),
                    *[str(age) for age in search_criteria.passengers_ages],
                ],
            ),
        )

    async def gather_search_results(  # noqa: C901,WPS210,WPS231
        self,
        search_criteria: request.CreateSearchRequest,
    ) -> AsyncIterator[offer_models_pb2.OfferGroup]:
        origin = self._train_stations.get_by_id(
            search_criteria.origin_id,
        )
        destination = self._train_stations.get_by_id(
            search_criteria.destination_id,
        )

        try:
            await self._client.get_general_search_results(
                request.GeneralSearchResultsRequest(
                    origin_id=origin.identifier,
                    destination_id=destination.identifier,
                    trip_type=enums.TripType.one_way,
                    number_of_passengers=len(search_criteria.passengers_ages),
                    departure_date=search_criteria.departure_datetime.date(),
                ),
            )
        except httpx.TimeoutException as timeout_error:
            self._logger.info("SAT timeout error occurred.", error=timeout_error)
        except httpx.HTTPStatusError as http_status_error:
            status_code = http_status_error.response.status_code
            if status_code != httpx.codes.INTERNAL_SERVER_ERROR:
                if http_status_error.response.text:
                    raise_http_error_with_text(http_status_error)
                raise http_status_error

        try:
            search_response = await self._client.create_search(search_criteria)
        except exceptions.SATValidationError as search_error:
            raise NoResultsError(search_error) from search_error
        except httpx.HTTPStatusError as http_error:
            if http_error.response.text:
                raise_http_error_with_text(http_error)
            raise http_error

        for search_result in search_response.search_results:
            try:
                search_details = await self._client.get_search_result_details(
                    request.SearchResultRequest(
                        search_id=search_response.identifier,
                        search_result_id=search_result.identifier,
                    ),
                )
            except exceptions.SATValidationError:
                continue
            except httpx.HTTPStatusError:
                continue

            expires_at = datetime.datetime.now(tz=datetime.timezone.utc) + self._ttl
            offer_segment_id = string.uuid()

            yield offer_models_pb2.OfferGroup(
                id=string.uuid(),
                expires_at=protobuf.datetime_to_protobuf(expires_at),
                offers=[
                    offer_models_pb2.Offer(
                        id=await self._offers_cache.store(
                            cache.OfferDetails(
                                search_id=search_response.identifier,
                                search_result_id=search_result.identifier,
                                transfer_id=transfer.identifier,
                                fare_id=transfer_fare.identifier,
                                price=transfer_fare.price,
                                currency="EUR",
                            ),
                            expires_at=expires_at,
                        ),
                        segment_details=[
                            offer_models_pb2.OfferSegmentDetails(
                                id=string.uuid(),
                                offer_segment_id=offer_segment_id,
                                cabin_class=models_pb2.CabinClass(
                                    type=await self._cabin_mapping.resolve_cabin_class(
                                        fare_brand=transfer_fare.name,
                                        operator=_resolve_train_operator(
                                            train_category=transfer_change.train.category,
                                            train_number=transfer_change.train.number,
                                        ),
                                    ),
                                    marketing_name=transfer_fare.name.replace(
                                        "_",
                                        " ",
                                    ).capitalize(),
                                ),
                            ),
                        ],
                        price=money.from_string(
                            string_amount=transfer_fare.price,
                            currency=money.Currency("EUR"),
                        ).protobuf(),
                        brand_name=transfer_fare.name.replace(
                            "_",
                            " ",
                        ).capitalize(),
                    )
                    for transfer in search_details.transfers
                    for transfer_fare, transfer_change in zip(
                        transfer.fares,
                        transfer.changes,
                        strict=True,
                    )
                ],
                segments=[
                    offer_models_pb2.OfferSegment(
                        id=offer_segment_id,
                        vehicle=offer_models_pb2.Vehicle(
                            number=transfer_change.train.number or "",
                        ),
                        vendor=transfer_change.train.category or "",
                        type=models_pb2.Schedule.TYPE_RAIL,
                        legs=[
                            offer_models_pb2.OfferSegmentLeg(
                                id=string.uuid(),
                                origin=models_pb2.Point(
                                    ref=origin.identifier,
                                    name=str(origin.name),
                                    coordinates=models_pb2.Coordinates(
                                        latitude=origin.latitude,
                                        longitude=origin.longitude,
                                    ),
                                    time_zone=origin.timezone.key,
                                ),
                                destination=models_pb2.Point(
                                    ref=destination.identifier,
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
        task: order_amqp_pb2.PlaceOrderTask,
        offer_details: cache.OfferDetails,
    ) -> order_models_pb2.Booking:
        new_booking = task.booking

        try:
            booking_responses = await self._create_booking(task, offer_details)
        except (
            phonenumbers.NumberParseException,
            BookingError,
            SaveATrainAdapterError,
        ) as error:
            self._logger.exception(
                "Booking failed",
                reason=repr(error),
            )
            new_booking.MergeFrom(
                order_models_pb2.Booking(
                    status=order_models_pb2.Booking.STATUS_ERROR,
                    raw_data=repr(error),
                ),
            )

            return new_booking

        await self._notifications_producer.publish(
            msg=amqp_pb2.BookingNotificationTask(
                journey_id=task.metadata.journey_id,
                order_id=task.metadata.order_id,
                booking_id=task.metadata.booking_id,
                passenger_name_record=task.metadata.passenger_name_record,
                search_identifier=booking_responses.make_booking.search_identifier,
                departure_at=booking_responses.make_booking.outbound_trip_info.departure.isoformat(
                    timespec="seconds",
                ),
                ticket_url=booking_responses.get_ticket.url,
            ),
            routing_key="notifications",
        )

        new_booking.MergeFrom(
            order_models_pb2.Booking(
                status=order_models_pb2.Booking.STATUS_CONFIRMED,
                total_price=money.from_string(
                    string_amount=booking_responses.make_booking.total_price,
                    currency=money.Currency("EUR"),
                ).protobuf(),
                trip_result=order_models_pb2.TripBooking(
                    provider_booking_reference=booking_responses.make_booking.search_identifier,
                    record_locator=booking_responses.get_ticket.confirmation_code,
                    created_at=protobuf.datetime_to_protobuf(
                        datetime.datetime.now(tz=datetime.timezone.utc),
                    ),
                ),
                raw_data=(
                    "{{makeBooking: {0}, confirmBooking: {1}, getTicket: {2}}}".format(
                        booking_responses.make_booking.json(),
                        booking_responses.confirm_booking.json(),
                        booking_responses.get_ticket.json(),
                    )
                ),
            ),
        )

        return new_booking

    async def get_ticket(
        self,
        search_id: str,
    ) -> booking.TicketInfo:
        try:
            return await self._client.get_ticket(search_id)
        except exceptions.SATValidationError as booking_error:
            raise BookingError(booking_error) from booking_error
        except httpx.HTTPStatusError as http_error:
            if http_error.response.text:
                raise_http_error_with_text(http_error)
            raise http_error

    async def _create_booking(
        self,
        task: order_amqp_pb2.PlaceOrderTask,
        offer_details: cache.OfferDetails,
    ) -> models.CombinedBookingResults:
        search_id, seat_code = self._extract_search_id_and_seat_preference_code(
            await self._select_search_result(offer_details),
        )
        booking_result = await self._make_booking(
            contact_details=task.contact_details,
            passengers=task.passengers,
            search_id=search_id,
            seat_code=seat_code,
        )
        confirm_booking_result = await self._confirm_booking(search_id=search_id)
        get_ticket_result = await self.get_ticket(search_id=search_id)
        return models.CombinedBookingResults(
            make_booking=booking_result,
            confirm_booking=confirm_booking_result,
            get_ticket=get_ticket_result,
        )

    async def _select_search_result(
        self,
        offer_details: cache.OfferDetails,
    ) -> search_result_selection.SearchResultSelectionResponse:
        try:
            return await self._client.select_search_result(
                request.SelectSearchResultRequest(
                    search_id=offer_details.search_id,
                    search_result_id=offer_details.search_result_id,
                    transfer_id=offer_details.transfer_id,
                    fare_id=offer_details.fare_id,
                ),
            )
        except exceptions.SATValidationError as search_error:
            raise BookingError(search_error) from search_error
        except httpx.HTTPStatusError as http_error:
            if http_error.response.text:
                raise_http_error_with_text(http_error)
            raise http_error

    def _extract_search_id_and_seat_preference_code(
        self,
        response: search_result_selection.SearchResultSelectionResponse,
    ) -> tuple[str, str | None]:
        seat_preference_code = None

        seat_preference = response.outbound_selected_result.seat_preference

        if seat_preference is not None:
            if seat_preference.status == "included":
                seat_preference_code = seat_preference.options[0].code
            else:
                seat_preference_code = next(
                    (
                        option.code
                        for option in seat_preference.options
                        if option.name == "notreserve"
                    ),
                    None,
                )

        return response.search_identifier, seat_preference_code

    async def _make_booking(
        self,
        contact_details: order_models_pb2.ContactDetails,
        passengers: Sequence[order_models_pb2.Passenger],
        search_id: str,
        seat_code: str | None,
    ) -> booking.BookingResult:
        title_map = {  # TODO: map unspecified to something else?
            order_models_pb2.Passenger.Title.TITLE_UNSPECIFIED: enums.PassengerTitle.mr,
            order_models_pb2.Passenger.Title.TITLE_MR: enums.PassengerTitle.mr,
            order_models_pb2.Passenger.Title.TITLE_MRS: enums.PassengerTitle.mrs,
            order_models_pb2.Passenger.Title.TITLE_MISS: enums.PassengerTitle.miss,
            order_models_pb2.Passenger.Title.TITLE_MS: enums.PassengerTitle.ms,
        }

        country = pycountry.countries.get(
            alpha_2=contact_details.address.region_code,
        )

        try:
            return await self._client.create_booking(
                request.CreateBookingRequest(
                    search_id=search_id,
                    seat_preference_code=seat_code or None,
                    passengers=[
                        booking.Passenger(
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
                            email=contact_details.email,
                            phone_number=str(
                                phonenumbers.parse(
                                    contact_details.phone.e164_number,
                                ).national_number,
                            ),
                            country=getattr(country, "common_name", country.name),
                        )
                        for passenger in passengers
                    ],
                ),
            )
        except exceptions.SATValidationError as booking_error:
            raise BookingError(booking_error) from booking_error
        except httpx.HTTPStatusError as http_error:
            if http_error.response.text:
                raise_http_error_with_text(http_error)
            raise http_error

    async def _confirm_booking(
        self,
        search_id: str,
    ) -> booking.BookingConfirmationResult:
        try:
            return await self._client.confirm_booking(search_id)
        except exceptions.SATValidationError as booking_error:
            raise BookingError(booking_error) from booking_error
        except httpx.HTTPStatusError as http_error:
            if http_error.response.text:
                raise_http_error_with_text(http_error)
            raise http_error


def raise_http_error_with_text(http_error: httpx.HTTPStatusError) -> None:
    raise SaveATrainAdapterError(
        "HTTPStatusError text: {0}".format(
            http_error.response.text,
        ),
    ) from http_error


def _resolve_train_operator(
    train_category: str | None,
    train_number: str | None,
) -> str | None:
    return train_category + train_number if train_category and train_number else None
