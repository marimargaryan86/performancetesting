from __future__ import annotations

import asyncio
import contextlib
import dataclasses
import datetime
from collections.abc import AsyncIterator, Iterable, Mapping, Sequence

import asyncstdlib

from snowfall.project.junction.go.service.offers.v1 import (
    models_pb2 as offer_models_pb2,
)
from snowfall.project.junction.go.v1 import models_pb2
from snowfall.project.junction.provider import cabin_classes
from snowfall.project.junction.service.providers.benerail import (
    cache,
    criteria,
    helper_functions,
    helper_models,
    train_stations,
)
from snowfall.project.junction.service.providers.benerail.constant import PROVIDER_ID
from snowfall.stdlib import money, string
from snowfall.stdlib.format import protobuf
from snowfall.stdlib.logging import stdout
from snowfall.stdlib.transport.http import errors
from snowfall.stdlib.v1 import latlng_pb2
from snowfall.vendor.benerail import client
from snowfall.vendor.benerail.models import types
from snowfall.vendor.benerail.models.dialogue import dialogue, passenger
from snowfall.vendor.benerail.models.trip_offers import link, offer
from snowfall.vendor.benerail.models.trip_offers import response as t_o_response
from snowfall.vendor.benerail.models.trips import trips

_NON_BOOKABLE_STATES = frozenset(("NOT_BOOKABLE_NO_SERVICE", "NOT_BOOKABLE_NO_PAST"))


class OfferNotFoundError(Exception):
    """Raised when failed to match the offer that was found during the offer search."""

    def __init__(
        self,
        trip_offer_responses: Sequence[t_o_response.GetTripOfferResponse] | None = None,
        offers: Sequence[offer.Offer] | None = None,
        message: str | None = None,
    ) -> None:
        super().__init__(message)

        self.offers = offers
        self.trip_offer_responses = trip_offer_responses


@dataclasses.dataclass(frozen=True)
class _CreatePassengersResponse(object):
    dialogue_etag: str
    passengers_info: list[helper_models.PassengerInfo]


@dataclasses.dataclass(frozen=True)
class _CreateTripFilterResponse(object):
    trip_filter_id: str
    dialogue_etag: str


@dataclasses.dataclass(frozen=True)
class _TripData(object):
    dialogue_id: str
    dialogue_etag: str
    create_passengers_response: _CreatePassengersResponse
    create_trip_filter_response: _CreateTripFilterResponse


@dataclasses.dataclass(frozen=True)
class _TripDataCriterion(object):
    origin: str
    destination: str
    departure_datetime: datetime.datetime
    passenger_dobs: Sequence[datetime.date]
    session_token: str | None = None


@dataclasses.dataclass(frozen=True)
class _TripOfferResponsesWithPassengers(object):
    passengers_info: Sequence[helper_models.PassengerInfo]
    trip_offer_responses: Sequence[t_o_response.GetTripOfferResponse]
    dialogue_info: helper_models.DialogueInfo


@dataclasses.dataclass(frozen=True)
class _TripOfferResponsesWithPassengersCriterion(object):
    origin: str
    destination: str
    outbound_departure_datetime: datetime.datetime
    passenger_dobs: Sequence[datetime.date]
    session_token: str | None = None


@dataclasses.dataclass(frozen=True)
class GetOfferResponse(object):
    offer_obj: offer.Offer
    dialogue_info: helper_models.DialogueInfo
    passengers_info: Sequence[helper_models.PassengerInfo]
    departure_at: str


class RCodeLabelNotFoundError(Exception):
    """Raised when rcode retrieval fails."""


def _get_trip_offer_response(
    trip_offer_responses: Sequence[t_o_response.GetTripOfferResponse],
    trip_id: str,
) -> t_o_response.GetTripOfferResponse:
    for trip_offer in trip_offer_responses:
        trip_href = trip_offer.response_result.trip.href

        if helper_functions.last_id_of_url(trip_href) == trip_id:
            return trip_offer

    raise OfferNotFoundError(
        trip_offer_responses=trip_offer_responses,
    )


class BenerailAdapter(object):
    def __init__(self, benerail_client: client.BenerailClient) -> None:
        self._client = benerail_client

    async def find_offer(
        self,
        offer_details: cache.OfferDetails,
    ) -> GetOfferResponse:
        trip_offer_responses_with_passengers = await self._get_trip_offer_responses_with_passengers(
            _TripOfferResponsesWithPassengersCriterion(
                origin=offer_details.origin_station,
                destination=offer_details.destination_station,
                outbound_departure_datetime=offer_details.outbound_departure_datetime,
                passenger_dobs=offer_details.passengers_dobs,
                session_token=offer_details.session_token,
            ),
        )

        if not trip_offer_responses_with_passengers.trip_offer_responses:
            raise OfferNotFoundError()

        trip_offer_obj = _get_trip_offer_response(
            trip_offer_responses=(
                trip_offer_responses_with_passengers.trip_offer_responses
            ),
            trip_id=offer_details.trip_id,
        )

        offers = await self._get_offers(
            offer_ids=[
                helper_functions.last_id_of_url(offer_ref.href)
                for offer_ref in trip_offer_obj.response_result.offers
            ],
            session_token=offer_details.session_token,
        )

        for offer_obj in offers:
            offer_matches = helper_functions.offer_matches(
                offer_obj=offer_obj,
                comfort_class_value=offer_details.comfort_class_value,
                flexibility_value=offer_details.flexibility_value,
            )

            if offer_matches:
                return GetOfferResponse(
                    offer_obj=offer_obj,
                    dialogue_info=trip_offer_responses_with_passengers.dialogue_info,
                    passengers_info=(
                        trip_offer_responses_with_passengers.passengers_info
                    ),
                    departure_at=str(trip_offer_obj.response_result.departure_at),
                )

        raise OfferNotFoundError(
            trip_offer_responses=(
                trip_offer_responses_with_passengers.trip_offer_responses
            ),
            offers=offers,
        )

    async def _get_trip_offer_responses_with_passengers(
        self,
        criterion: _TripOfferResponsesWithPassengersCriterion,
    ) -> _TripOfferResponsesWithPassengers:
        trip_filter_creation = await self._dialogue_with_passengers_and_trip_filter(
            _TripDataCriterion(
                origin=criterion.origin,
                destination=criterion.destination,
                departure_datetime=criterion.outbound_departure_datetime,
                passenger_dobs=criterion.passenger_dobs,
                session_token=criterion.session_token,
            ),
        )

        trip_offer_filter = await self._client.trip_offer_filter_client.create_trip_offer_filter(
            dialogue_id=trip_filter_creation.dialogue_id,
            etag=trip_filter_creation.dialogue_etag,
            body=dialogue.DialogueIdTripofferfiltersBody(
                trip_filter_id=trip_filter_creation.create_trip_filter_response.trip_filter_id,
                passengers=[
                    pax_info.identifier
                    for pax_info in trip_filter_creation.create_passengers_response.passengers_info
                ],
            ),
            session_token=criterion.session_token,
        )

        trip_offers_iterator = self._get_trips_of_offer_collection(
            collection_id=trip_offer_filter.response_result.identifier,
            session_token=criterion.session_token,
        )

        trip_offer_ids = [
            helper_functions.last_id_of_url(trip_offer.href)
            async for trip_offer in trip_offers_iterator
        ]
        dialogue_info = helper_models.DialogueInfo(
            identifier=trip_filter_creation.dialogue_id,
            etag=trip_filter_creation.dialogue_etag,
        )

        if not trip_offer_ids:
            return _TripOfferResponsesWithPassengers(
                passengers_info=[],
                trip_offer_responses=[],
                dialogue_info=dialogue_info,
            )

        trip_offer_responses_iterator = self._get_trip_offers(
            trip_offer_ids=trip_offer_ids,
            session_token=criterion.session_token,
        )

        return _TripOfferResponsesWithPassengers(
            trip_offer_responses=[
                trip_offer_res
                for trip_offer_res in await trip_offer_responses_iterator
                if trip_offer_res.response_result.offers
            ],
            passengers_info=(
                trip_filter_creation.create_passengers_response.passengers_info
            ),
            dialogue_info=dialogue_info,
        )

    async def _dialogue_with_passengers_and_trip_filter(
        self,
        criterion: _TripDataCriterion,
    ) -> _TripData:
        dialogue_res = await self._client.dialogue.create_dialogue(
            session_token=criterion.session_token,
        )
        dialogue_id = dialogue_res.response_result.identifier

        create_passenger_res = await self._create_passengers(
            dialogue_info=helper_models.DialogueInfo(
                identifier=dialogue_id,
                etag=dialogue_res.etag,
            ),
            passenger_dobs=criterion.passenger_dobs,
            session_token=criterion.session_token,
        )
        create_trip_filter_res = await self._create_trip_filter(
            dialogue_info=helper_models.DialogueInfo(
                identifier=dialogue_id,
                etag=create_passenger_res.dialogue_etag,
            ),
            origin=criterion.origin,
            destination=criterion.destination,
            departure_datetime=criterion.departure_datetime,
            session_token=criterion.session_token,
        )

        return _TripData(
            dialogue_id=dialogue_id,
            dialogue_etag=create_trip_filter_res.dialogue_etag,
            create_passengers_response=create_passenger_res,
            create_trip_filter_response=create_trip_filter_res,
        )

    async def _create_passengers(
        self,
        dialogue_info: helper_models.DialogueInfo,
        passenger_dobs: Sequence[datetime.date],
        session_token: str | None = None,
    ) -> _CreatePassengersResponse:
        passengers_info = []
        passenger_etags = {}
        etag = dialogue_info.etag

        for date_of_birth in passenger_dobs:
            passenger_res = await self._client.passengers_client.create_passenger(
                dialogue_id=dialogue_info.identifier,
                etag=etag,
                body=passenger.PassengerRequest(
                    date_of_birth=date_of_birth,
                ),
                session_token=session_token,
            )
            etag = passenger_res.etag
            passenger_etags[passenger_res.response_result.identifier] = (
                passenger_res.metadata.resource_etag or ""
            )
            passengers_info.append(
                helper_models.PassengerInfo(
                    identifier=passenger_res.response_result.identifier,
                    etag=passenger_res.metadata.resource_etag or "",
                    date_of_birth=date_of_birth,
                ),
            )

        return _CreatePassengersResponse(
            passengers_info=passengers_info,
            dialogue_etag=etag,
        )

    async def _create_trip_filter(
        self,
        dialogue_info: helper_models.DialogueInfo,
        origin: str,
        destination: str,
        departure_datetime: datetime.datetime,
        session_token: str | None = None,
    ) -> _CreateTripFilterResponse:
        trip_filter_res = await self._client.trip_filter.create_trip_filter(
            dialogue_id=dialogue_info.identifier,
            etag=dialogue_info.etag,
            body=dialogue.DialogueIdTripfiltersBody(
                origin=types.PlaceUrnStr(origin),
                destination=types.PlaceUrnStr(destination),
                departure_date_time=types.ZonedDatetimeStr(
                    departure_datetime.isoformat(
                        timespec="minutes",
                    ),
                ),
            ),
            session_token=session_token,
        )

        return _CreateTripFilterResponse(
            trip_filter_id=trip_filter_res.response_result.identifier,
            dialogue_etag=trip_filter_res.etag,
        )

    async def _get_trips_of_offer_collection(
        self,
        collection_id: str,
        session_token: str | None = None,
    ) -> AsyncIterator[link.TripOfferResourceLink]:
        get_coll = self._client.trip_offers_client.get_trip_offer_ids_in_collection
        collection = await get_coll(
            trip_offer_collection_id=collection_id,
            session_token=session_token,
        )

        if not collection.response_result.trip_offers:
            return

        for trip_offer in collection.response_result.trip_offers:
            summary = trip_offer.summary

            if summary is None:
                continue

            if summary.bookable_status.status_value not in _NON_BOOKABLE_STATES:
                yield trip_offer

    async def _get_trip_offers(
        self,
        trip_offer_ids: Sequence[str],
        session_token: str | None = None,
    ) -> list[t_o_response.GetTripOfferResponse]:
        return await asyncio.gather(
            *(
                self._client.trip_offers_client.get_trip_offer_info(
                    trip_offer_id=trip_offer_id,
                    session_token=session_token,
                )
                for trip_offer_id in trip_offer_ids
            ),
        )

    async def _get_offers(
        self,
        offer_ids: Iterable[str],
        session_token: str | None = None,
    ) -> list[offer.Offer]:
        responses = await asyncio.gather(
            *(
                self._client.offers_client.get_offer_info(
                    offer_id,
                    session_token,
                )
                for offer_id in offer_ids
            ),
        )

        return [response.response_result for response in responses]


class BenerailOffersAdapter(BenerailAdapter):
    def __init__(
        self,
        benerail_client: client.BenerailClient,
        train_station_repository: train_stations.TrainStationRepository,
        offers_cache: cache.OffersCache,
        ttl: datetime.timedelta,
        provider_cabin_class_mapping: cabin_classes.CabinMappingRepository,
    ) -> None:
        super().__init__(benerail_client)
        self._train_stations = train_station_repository
        self._cabin_mapping = provider_cabin_class_mapping
        self._offers_cache = offers_cache
        self._ttl = ttl
        self._logger = stdout.get_logger()

    async def gather_search_results(
        self,
        search_task: criteria.SearchCriteria,
    ) -> AsyncIterator[offer_models_pb2.OfferGroup]:
        try:
            async for offer_group in self._get_offer_groups(search_task):
                yield offer_group
        except errors.HttpError:
            self._logger.exception(
                "Offer search failed",
                session_token=search_task.session_token,
            )

    async def _get_offer_groups(  # noqa: WPS217
        self,
        search_task: criteria.SearchCriteria,
    ) -> AsyncIterator[offer_models_pb2.OfferGroup]:
        trip_offer_responses_with_passengers = (
            await self._get_trip_offer_responses_with_passengers(
                criterion=_TripOfferResponsesWithPassengersCriterion(
                    origin=search_task.origin,
                    destination=search_task.destination,
                    outbound_departure_datetime=search_task.outbound_departure_datetime,
                    passenger_dobs=search_task.passenger_dobs,
                    session_token=search_task.session_token,
                ),
            )
        )
        trip_offer_responses = trip_offer_responses_with_passengers.trip_offer_responses
        passengers_info = trip_offer_responses_with_passengers.passengers_info

        if not trip_offer_responses or not passengers_info:
            return

        trip_id_offer_ids = tuple(
            (
                helper_functions.last_id_of_url(
                    trip_offer_res.response_result.trip.href,
                ),
                tuple(
                    helper_functions.last_id_of_url(offer_link.href)
                    for offer_link in trip_offer_res.response_result.offers
                ),
            )
            for trip_offer_res in trip_offer_responses
        )

        offer_map = {
            offer_info.identifier: offer_info
            for offer_info in await self._get_offers(
                offer_ids=(
                    offer_id
                    for _, offer_ids in trip_id_offer_ids
                    for offer_id in offer_ids
                ),
                session_token=search_task.session_token,
            )
        }

        trip_map = await self._get_trip_map(
            trip_ids=(trip_id for trip_id, _ in trip_id_offer_ids),
            session_token=search_task.session_token,
        )

        expires_at_dt = datetime.datetime.now(datetime.UTC) + self._ttl

        for trip_id, offer_ids in trip_id_offer_ids:
            try:
                trip = trip_map[trip_id]
            except KeyError:
                self._logger.warning(
                    "Trip info not found, skipping offers",
                    offer_ids=offer_ids,
                    trip_id=trip_id,
                )

                continue

            timed_legs_count = len(
                [leg for leg in trip.trip_legs if isinstance(leg, trips.TimedLeg)],
            )
            segment_ids = [string.uuid() for _ in range(timed_legs_count)]

            offers = []

            for offer_id in offer_ids:
                offer_model = await self._parse_offer(
                    offer_obj=offer_map[offer_id],
                    offer_segment_ids=segment_ids,
                )

                await self._offers_cache.store(
                    cache.OfferDetails(
                        passengers_dobs=[pax.date_of_birth for pax in passengers_info],
                        origin_station=trip.origin.place_value,
                        destination_station=trip.destination.place_value,
                        trip_id=trip_id,
                        outbound_departure_datetime=(
                            search_task.outbound_departure_datetime
                        ),
                        comfort_class_value=helper_functions.get_comfort_class_value(
                            offer_obj=offer_map[offer_id],
                        ),
                        flexibility_value=(
                            offer_map[offer_id].flexibility.flexibility_value
                        ),
                        session_token=search_task.session_token,
                    ),
                    expires_at=expires_at_dt,
                    key=offer_model.id,
                )

                offers.append(offer_model)

            yield offer_models_pb2.OfferGroup(
                id=string.uuid(),
                expires_at=protobuf.datetime_to_protobuf(expires_at_dt),
                offers=offers,
                segments=await self._parse_segments(trip, segment_ids),
                provider_id=str(PROVIDER_ID),
            )

    async def _get_train_type(self, leg: trips.TimedLeg) -> str:
        if leg.train_type and leg.train_type.train_type_value:
            train_type = leg.train_type.train_type_value

            try:
                return await self._resolve_rcode_title(
                    train_type,
                )
            except RCodeLabelNotFoundError:
                return train_type.rsplit(":", 1)[-1]

        return ""

    async def _parse_segments(
        self,
        trip: trips.Trip,
        segment_ids: Sequence[str],
    ) -> list[offer_models_pb2.OfferSegment]:
        segments = []
        timed_legs = [leg for leg in trip.trip_legs if isinstance(leg, trips.TimedLeg)]

        for idx, leg in enumerate(timed_legs):
            segments.append(
                offer_models_pb2.OfferSegment(
                    id=segment_ids[idx],
                    legs=[self._parse_leg_info(leg)],
                    vehicle=offer_models_pb2.Vehicle(
                        number=helper_functions.get_train_number(leg),
                    ),
                    vendor=await self._get_train_type(leg),
                    type=models_pb2.Schedule.TYPE_RAIL,
                ),
            )

        return segments

    def _parse_leg_info(
        self,
        timed_leg: trips.TimedLeg,
    ) -> offer_models_pb2.OfferSegmentLeg:
        origin = self._train_stations.resolve_place_with_urn(
            timed_leg.origin.place_value,
        )

        destination = self._train_stations.resolve_place_with_urn(
            timed_leg.destination.place_value,
        )

        return offer_models_pb2.OfferSegmentLeg(
            id=string.uuid(),
            origin=models_pb2.Point(
                ref=origin.identifier,
                name=origin.name.title() if origin.name else "",
                coordinates=latlng_pb2.LatLng(
                    latitude=origin.latitude,
                    longitude=origin.longitude,
                ),
                time_zone=origin.timezone.key,
            ),
            destination=models_pb2.Point(
                ref=destination.identifier,
                name=destination.name.title() if destination.name else "",
                coordinates=latlng_pb2.LatLng(
                    latitude=destination.latitude,
                    longitude=destination.longitude,
                ),
                time_zone=destination.timezone.key,
            ),
            departure_at=(
                protobuf.datetime_to_protobuf(
                    datetime.datetime.strptime(
                        timed_leg.departure_at,
                        "%Y-%m-%dT%H:%M:%S%z",
                    ),
                )
            ),
            arrival_at=(
                protobuf.datetime_to_protobuf(
                    datetime.datetime.strptime(
                        timed_leg.arrival_at,
                        "%Y-%m-%dT%H:%M:%S%z",
                    ),
                )
            ),
        )

    async def _parse_offer(
        self,
        offer_obj: offer.Offer,
        offer_segment_ids: Sequence[str],
    ) -> offer_models_pb2.Offer:
        comfort_class_value = helper_functions.get_comfort_class_value(offer_obj)

        price_proto = money.from_string(
            string_amount=str(offer_obj.price.amount),
            currency=money.Currency(
                offer_obj.price.currency.upper(),
            ),
        ).protobuf()

        if comfort_class_value:
            try:
                comfort_class_name = await self._resolve_rcode_title(
                    comfort_class_value,
                )
            except RCodeLabelNotFoundError:
                comfort_class_name = comfort_class_value
        else:
            comfort_class_name = ""

        return offer_models_pb2.Offer(
            id=string.uuid(),
            segment_details=[
                offer_models_pb2.OfferSegmentDetails(
                    id=string.uuid(),
                    offer_segment_id=offer_segment_id,
                    cabin_class=models_pb2.CabinClass(
                        type=await self._cabin_mapping.resolve_cabin_class(
                            comfort_class_value,
                            "benerail",
                        ),
                        marketing_name=comfort_class_name,
                    ),
                )
                for offer_segment_id in offer_segment_ids
            ],
            price=price_proto,
            price_breakdown=[
                offer_models_pb2.PriceBreakdown(
                    price=price_proto,
                    breakdown_type=offer_models_pb2.PriceBreakdown.BreakdownType.BREAKDOWN_TYPE_BASE_FARE,
                ),
            ],
            brand_name=helper_functions.get_brand_name(
                comfort_class_name=comfort_class_name,
                flexibility_value=offer_obj.flexibility.flexibility_value,
            ),
        )

    @asyncstdlib.lru_cache()
    async def _resolve_rcode_title(self, rcode_value: str) -> str:
        try:
            urn_val = await self._client.rcode_client.get_urn_value(rcode_value)
        except errors.HttpError as http_error_ex:
            raise RCodeLabelNotFoundError from http_error_ex

        label_obj = None

        for rcode_obj in urn_val.response_result.rcodes:
            with contextlib.suppress(KeyError):
                label_obj = helper_functions.get_rcode_label(rcode_obj.labels)

            if label_obj:
                break

        if not label_obj:
            raise RCodeLabelNotFoundError

        label = label_obj.code_long or label_obj.code_short

        if not label:
            raise RCodeLabelNotFoundError

        return label

    async def _get_trip_map(
        self,
        trip_ids: Iterable[str],
        session_token: str | None = None,
    ) -> Mapping[str, trips.Trip]:
        get_trip_coroutines = [
            self._client.trips_client.get_trip(
                trip_id=trip_id,
                session_token=session_token,
            )
            for trip_id in trip_ids
        ]

        trip_map = {}

        for get_trip_coroutine in asyncio.as_completed(get_trip_coroutines):
            try:
                get_trip_response = await get_trip_coroutine
            except errors.HttpError as ex:
                self._logger.warning(
                    "Failed to get the trip",
                    request=ex.request,
                    response=ex.response,
                )

                continue

            trip_map[
                get_trip_response.response_result.identifier
            ] = get_trip_response.response_result

        return trip_map
