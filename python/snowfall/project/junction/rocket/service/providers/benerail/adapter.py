from __future__ import annotations

import asyncio
import contextlib
import dataclasses
import datetime
from collections.abc import AsyncIterator, Iterable, Mapping, Sequence

import asyncstdlib

from snowfall.project.junction.go.v1 import models_pb2 as legacy_models_pb2
from snowfall.project.junction.rocket.provider import cabin_classes
from snowfall.project.junction.rocket.service.providers.benerail import (
    cache,
    helper_functions,
    helper_models,
    searches,
    train_stations,
)
from snowfall.project.junction.rocket.service.providers.benerail.constant import (
    PROVIDER_ID,
)
from snowfall.project.junction.rocket.service.searches.v1alpha import models_pb2
from snowfall.stdlib import money, string
from snowfall.stdlib.format import protobuf
from snowfall.stdlib.logging import stdout
from snowfall.stdlib.transport.http import errors
from snowfall.stdlib.v1 import latlng_pb2
from snowfall.vendor.benerail import client
from snowfall.vendor.benerail.models import types
from snowfall.vendor.benerail.models.dialogue import dialogue, passenger
from snowfall.vendor.benerail.models.trip_offers import link, offer, summary
from snowfall.vendor.benerail.models.trip_offers import response as t_o_response
from snowfall.vendor.benerail.models.trips import trips

_NON_BOOKABLE_STATES = frozenset(("NOT_BOOKABLE_NO_SERVICE", "NOT_BOOKABLE_NO_PAST"))
_BENERAIL_PUBLIC_FARES_CODE = "urn:bnds:market_segment_preference:REQ_PUBLIC"


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
class _GetOfferResponse:
    offer_obj: offer.Offer
    dialogue_info: helper_models.DialogueInfo
    passengers_info: Sequence[helper_models.PassengerInfo]
    departure_at: str


@dataclasses.dataclass(frozen=True)
class _CreatePassengersResponse:
    dialogue_etag: str
    passengers_info: list[helper_models.PassengerInfo]


@dataclasses.dataclass(frozen=True)
class _CreateTripFilterResponse:
    trip_filter_id: str
    dialogue_etag: str


@dataclasses.dataclass(frozen=True)
class _TripDataCriterion:
    origin: str
    destination: str
    departure_datetime: datetime.datetime
    passenger_dobs: Sequence[datetime.date]
    session_token: str | None = None


@dataclasses.dataclass(frozen=True)
class _TripData:
    dialogue_id: str
    dialogue_etag: str
    create_passengers_response: _CreatePassengersResponse
    create_trip_filter_response: _CreateTripFilterResponse


@dataclasses.dataclass(frozen=True)
class _ProcessTripFilterResult:
    dialogue_id: str
    trip_filter_id: str
    etag: str
    passenger_ids: Sequence[str]
    passengers_info: Sequence[helper_models.PassengerInfo]


@dataclasses.dataclass(frozen=True)
class _TripOfferResponsesWithPassengersCriterion:
    origin: str
    destination: str
    outbound_departure_datetime: datetime.datetime
    passenger_dobs: Sequence[datetime.date]
    outbound_offer_id: str | None = None
    session_token: str | None = None
    return_departure_after: datetime.datetime | None = None


@dataclasses.dataclass(frozen=True)
class _TripOfferResponsesWithPassengers:
    passengers_info: Sequence[helper_models.PassengerInfo]
    trip_offer_responses: Sequence[t_o_response.GetTripOfferResponse]
    dialogue_info: helper_models.DialogueInfo
    trip_offer_filter_id: str


@dataclasses.dataclass(frozen=True)
class _TimedSegment:
    id: str
    segment: trips.TimedLeg


class RCodeLabelNotFoundError(Exception):
    """Raised when rcode retrieval fails."""


def _compare_trip_offer_response(
    trip_offer_responses: Sequence[t_o_response.GetTripOfferResponse],
    trip_id: str,
) -> t_o_response.GetTripOfferResponse:
    for trip_offer in trip_offer_responses:
        if trip_offer.response_result.trip.identifier == trip_id:
            return trip_offer

    raise OfferNotFoundError(
        trip_offer_responses=trip_offer_responses,
    )


class BenerailAdapter:
    def __init__(self, benerail_client: client.BenerailClient) -> None:
        self._client = benerail_client

    async def verify_offer(
        self,
        offer_details: cache.OfferDetails,
        session_token: str | None = None,
    ) -> _GetOfferResponse:
        trip_offer_responses_with_passengers = (
            await self._get_trip_offers_by_offer_filter_id(
                offer_details.outward_passengers_info,
                offer_details.trip_offer_filter_id,
                offer_details.dialogue_id,
                offer_details.dialogue_etag,
            )
        )

        if not trip_offer_responses_with_passengers.trip_offer_responses:
            raise OfferNotFoundError()
        trip_offer_obj = _compare_trip_offer_response(
            trip_offer_responses=(
                trip_offer_responses_with_passengers.trip_offer_responses
            ),
            trip_id=offer_details.trip_id,
        )

        offers, _ = await self._get_offers(
            offer_ids=[
                offer_ref.identifier
                for offer_ref in trip_offer_obj.response_result.offers
            ],
            session_token=session_token,
        )

        for offer_obj in offers:
            offer_matches = helper_functions.offer_matches(
                offer_obj=offer_obj,
                comfort_class_value=offer_details.comfort_class_value,
                flexibility_value=offer_details.flexibility_value,
            )

            if offer_matches:
                return _GetOfferResponse(
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

    async def _get_offers(
        self,
        offer_ids: Iterable[str],
        session_token: str | None = None,
    ) -> tuple[list[offer.Offer], set[str]]:
        responses = await asyncio.gather(
            *(
                self._client.offers_client.get_offer_info(
                    offer_id,
                    session_token,
                )
                for offer_id in offer_ids
            ),
        )
        offers = []
        excluded_ids = set()

        for response in responses:
            if response.response_result.price.currency == "?":
                excluded_ids.add(response.response_result.identifier)
            else:
                offers.append(response.response_result)

        return offers, excluded_ids

    def _create_dialogue_body(
        self,
        trip_filter_id: str,
        passenger_ids: Sequence[str],
        return_trip_params: dialogue.DialogueIdTripOfferFiltersReturnTripParams,
    ) -> dialogue.DialogueIdTripofferfiltersBody:
        return dialogue.DialogueIdTripofferfiltersBody(
            trip_filter_id=trip_filter_id,
            passengers=passenger_ids,
            return_trip_params=return_trip_params,
            market_segment=dialogue.MarketSegment(code=_BENERAIL_PUBLIC_FARES_CODE),
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

    async def _get_dialogue_with_passengers_and_trip_filter(
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

    async def _process_trip_filter(
        self,
        criterion: _TripOfferResponsesWithPassengersCriterion,
    ) -> _ProcessTripFilterResult:
        trip_filter = await self._get_dialogue_with_passengers_and_trip_filter(
            _TripDataCriterion(
                origin=criterion.origin,
                destination=criterion.destination,
                departure_datetime=criterion.outbound_departure_datetime,
                passenger_dobs=criterion.passenger_dobs,
                session_token=criterion.session_token,
            ),
        )
        dialogue_id = trip_filter.dialogue_id
        trip_filter_id = trip_filter.create_trip_filter_response.trip_filter_id
        etag = trip_filter.dialogue_etag
        passenger_ids = [
            pax_info.identifier
            for pax_info in trip_filter.create_passengers_response.passengers_info
        ]
        passengers_info = trip_filter.create_passengers_response.passengers_info
        return _ProcessTripFilterResult(
            dialogue_id,
            trip_filter_id,
            etag,
            passenger_ids,
            passengers_info,
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
            if trip_offer.summary is None:
                continue

            if (  # noqa: WPS337
                trip_offer.summary.bookable_status.status_value
                not in _NON_BOOKABLE_STATES
            ):
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

    async def _get_trip_offers_by_offer_filter_id(
        self,
        passenger_info: Sequence[helper_models.PassengerInfo],
        trip_offer_filter_id: str,
        dialogue_id: str,
        dialogue_etag: str,
    ) -> _TripOfferResponsesWithPassengers:
        trip_offers_iterator = self._get_trips_of_offer_collection(
            collection_id=trip_offer_filter_id,
        )

        trip_offer_ids = [
            trip_offer.identifier async for trip_offer in trip_offers_iterator
        ]
        dialogue_info = helper_models.DialogueInfo(
            identifier=dialogue_id,
            etag=dialogue_etag,
        )

        if not trip_offer_ids:
            return _TripOfferResponsesWithPassengers(
                passengers_info=[],
                trip_offer_responses=[],
                dialogue_info=dialogue_info,
                trip_offer_filter_id=trip_offer_filter_id,
            )

        trip_offer_responses_iterator = self._get_trip_offers(
            trip_offer_ids=trip_offer_ids,
        )
        return _TripOfferResponsesWithPassengers(
            trip_offer_responses=[
                trip_offer_res
                for trip_offer_res in await trip_offer_responses_iterator
                if trip_offer_res.response_result.offers
            ],
            passengers_info=passenger_info,
            dialogue_info=dialogue_info,
            trip_offer_filter_id=trip_offer_filter_id,
        )

    async def _handle_passenger_criterion(
        self,
        criterion: _TripOfferResponsesWithPassengersCriterion,
        trip_filter_result: _ProcessTripFilterResult,
    ) -> str:
        return_trip_params = dialogue.DialogueIdTripOfferFiltersReturnTripParams(
            inward_date_time=(
                criterion.return_departure_after.isoformat(
                    timespec="seconds",
                )
                if criterion.return_departure_after
                else None
            ),
            outward_offer_id=criterion.outbound_offer_id or None,
        )
        body = self._create_dialogue_body(
            trip_filter_result.trip_filter_id,
            trip_filter_result.passenger_ids,
            return_trip_params,
        )
        trip_offer_filter = (
            await self._client.trip_offer_filter_client.create_trip_offer_filter(
                dialogue_id=trip_filter_result.dialogue_id,
                etag=trip_filter_result.etag,
                body=body,
                session_token=criterion.session_token,
            )
        )
        return trip_offer_filter.response_result.identifier

    async def _get_trip_offer_responses_with_passengers(
        self,
        criterion: _TripOfferResponsesWithPassengersCriterion,
    ) -> _TripOfferResponsesWithPassengers:
        offer_process_result = await self._process_trip_filter(criterion)

        trip_offer_filter_id = await self._handle_passenger_criterion(
            criterion,
            offer_process_result,
        )

        return await self._get_trip_offers_by_offer_filter_id(
            offer_process_result.passengers_info,
            trip_offer_filter_id,
            offer_process_result.dialogue_id,
            offer_process_result.etag,
        )


class BenerailOffersAdapter(BenerailAdapter):
    def __init__(
        self,
        benerail_client: client.BenerailClient,
        train_station_repository: train_stations.TrainStationRepository,
        offers_cache: cache.OffersCache,
        ttl: datetime.timedelta,
        provider_cabin_class_mapping: cabin_classes.CabinMappingRepository,
        pay_company_id: str,
    ) -> None:
        super().__init__(benerail_client)
        self._train_stations = train_station_repository
        self._cabin_mapping = provider_cabin_class_mapping
        self._offers_cache = offers_cache
        self._ttl = ttl
        self._logger = stdout.get_logger()
        self._pay_company_id = pay_company_id

    async def gather_search_results(
        self,
        search_task: searches.Criteria,
    ) -> AsyncIterator[models_pb2.SearchResult]:
        try:
            async for result in self._get_search_results(search_task):
                yield result
        except errors.HttpError:
            self._logger.exception(
                "Offer search failed",
                session_token=search_task.session_token,
            )

    async def _fetch_and_process_outward_offer_details(
        self,
        search_task: searches.Criteria,
    ) -> cache.OfferDetails | None:
        outward_offer_details = None
        if search_task.outbound_offer_id:
            outward_offer_details = await self._offers_cache.fetch(
                search_task.outbound_offer_id,
            )
        if outward_offer_details:
            return outward_offer_details
        return None

    async def _parse_criterion(
        self,
        search_task: searches.Criteria,
    ) -> _TripOfferResponsesWithPassengersCriterion:
        outward_trip_info = await self._fetch_and_process_outward_offer_details(
            search_task,
        )

        return _TripOfferResponsesWithPassengersCriterion(
            origin=search_task.origin,
            destination=search_task.destination,
            outbound_departure_datetime=search_task.outbound_departure_datetime,
            passenger_dobs=search_task.passenger_dobs,
            session_token=search_task.session_token,
            outbound_offer_id=(
                outward_trip_info.outward_offer_id if outward_trip_info else None
            ),
            return_departure_after=search_task.return_departure_after,
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

            trip_map[get_trip_response.response_result.identifier] = (
                get_trip_response.response_result
            )

        return trip_map

    async def _get_search_results(  # noqa: WPS217 , WPS231
        self,
        search_task: searches.Criteria,
    ) -> AsyncIterator[models_pb2.SearchResult]:
        outward_trip_info = await self._fetch_and_process_outward_offer_details(
            search_task,
        )

        if search_task.outbound_offer_id and not outward_trip_info:
            raise OfferNotFoundError(message="Selected outbound offer not found.")

        criterion = await self._parse_criterion(search_task)

        trip_offer_responses_with_passengers = (
            await self._get_trip_offer_responses_with_passengers(criterion=criterion)
        )
        trip_offer_responses = trip_offer_responses_with_passengers.trip_offer_responses
        passengers_info = trip_offer_responses_with_passengers.passengers_info

        if not all((trip_offer_responses, passengers_info)):
            return

        expires_at_dt = datetime.datetime.now(datetime.UTC) + self._ttl
        trip_ids = [res.response_result.trip.identifier for res in trip_offer_responses]
        trip_map = await self._get_trip_map(trip_ids, search_task.session_token)

        for trip_offer_response in trip_offer_responses:
            trip_id = trip_offer_response.response_result.trip.identifier
            try:
                trip = trip_map[trip_id]
            except KeyError:
                self._logger.warning(
                    "Trip info not found, skipping trip offer",
                    trip_offer_response=trip_offer_response,
                )

                continue

            details_list = [
                _TimedSegment(id=string.uuid(), segment=segment)
                for segment in trip.trip_legs
                if isinstance(segment, trips.TimedLeg)
            ]

            offer_protos = []
            search_result_id = string.uuid()
            for offer_obj in trip_offer_response.response_result.offers:
                cur = offer_obj.summary.price_with_optional_parts.currency.upper()
                try:
                    self._parse_currency(cur)
                except ValueError:
                    continue

                offer_model = await self._parse_offer(
                    offer_summary=offer_obj.summary,
                    details_list=details_list,
                )

                outward_passengers_info = [
                    helper_models.PassengerInfo(
                        identifier=pax.identifier,
                        etag=pax.etag,
                        date_of_birth=pax.date_of_birth,
                    )
                    for pax in passengers_info
                ]

                dialogue_id = (
                    trip_offer_responses_with_passengers.dialogue_info.identifier
                )
                if outward_trip_info and outward_trip_info.dialogue_id:
                    dialogue_id = outward_trip_info.dialogue_id

                await self._offers_cache.store(
                    cache.OfferDetails(
                        passengers_dobs=[pax.date_of_birth for pax in passengers_info],
                        outward_passengers_info=outward_trip_info.outward_passengers_info
                        if outward_trip_info
                        else outward_passengers_info,
                        dialogue_id=dialogue_id,
                        dialogue_etag=trip_offer_responses_with_passengers.dialogue_info.etag,
                        origin_station=trip.origin.place_value,
                        destination_station=trip.destination.place_value,
                        trip_id=trip_id,
                        outward_offer_id=offer_obj.identifier,
                        outbound_departure_datetime=search_task.outbound_departure_datetime,
                        trip_offer_filter_id=trip_offer_responses_with_passengers.trip_offer_filter_id,
                        comfort_class_value=helper_functions.get_comfort_class_value(
                            offer_obj.summary,
                        ),
                        flexibility_value=helper_functions.get_flexibility_value(
                            offer_obj.summary,
                        ),
                    ),
                    expires_at=expires_at_dt,
                    key=offer_model.id,
                )
                offer_protos.append(offer_model)
            yield models_pb2.SearchResult(
                id=search_result_id,
                expires_at=protobuf.datetime_to_protobuf(expires_at_dt),
                offers=offer_protos,
                result_details=await self._parse_result_details(
                    search_task.outbound_offer_id,
                    details_list,
                ),
                provider_id=str(PROVIDER_ID),
                pay_company_id=self._pay_company_id,
            )

    async def _parse_result_details(
        self,
        is_outbound_segment: str | None,
        details_list: Sequence[_TimedSegment],
    ) -> Sequence[models_pb2.ResultDetail]:
        result_details = []
        for idx, detail in enumerate(details_list):
            origin = self._train_stations.resolve_place_with_urn(
                detail.segment.origin.place_value,
            )
            destination = self._train_stations.resolve_place_with_urn(
                detail.segment.destination.place_value,
            )

            result_details.append(
                models_pb2.ResultDetail(
                    id=detail.id,
                    rail=models_pb2.RailResultDetail(
                        origin=legacy_models_pb2.Point(
                            ref=origin.identifier,
                            name=origin.name.title() if origin.name else "",
                            coordinates=latlng_pb2.LatLng(
                                latitude=origin.latitude,
                                longitude=origin.longitude,
                            ),
                            time_zone=origin.timezone.key,
                        ),
                        destination=legacy_models_pb2.Point(
                            ref=destination.identifier,
                            name=destination.name.title() if destination.name else "",
                            coordinates=latlng_pb2.LatLng(
                                latitude=destination.latitude,
                                longitude=destination.longitude,
                            ),
                            time_zone=destination.timezone.key,
                        ),
                        outbound_segment=not bool(is_outbound_segment),
                        segment_sequence=idx + 1,
                        departure_date=protobuf.datetime_to_protobuf_datetime(
                            datetime.datetime.strptime(
                                detail.segment.departure_at,
                                "%Y-%m-%dT%H:%M:%S%z",
                            ),
                        ),
                        arrival_date=protobuf.datetime_to_protobuf_datetime(
                            datetime.datetime.strptime(
                                detail.segment.arrival_at,
                                "%Y-%m-%dT%H:%M:%S%z",
                            ),
                        ),
                    ),
                ),
            )

        return result_details

    def _parse_currency(self, currency_string: str) -> money.Currency:
        return money.Currency(
            currency_string,
        )

    async def _parse_offer(
        self,
        offer_summary: summary.OfferSummary,
        details_list: Sequence[_TimedSegment],
    ) -> models_pb2.Offer:
        detail_ids = [detail.id for detail in details_list]

        comfort_class_value = helper_functions.get_comfort_class_value(
            offer_summary,
        )
        if comfort_class_value:
            try:
                comfort_class_name = await self._resolve_rcode_title(
                    comfort_class_value,
                )
            except RCodeLabelNotFoundError:
                comfort_class_name = comfort_class_value
        else:
            comfort_class_name = ""

        currency = self._parse_currency(
            offer_summary.price_with_optional_parts.currency.upper(),
        )

        price_proto = money.from_string(
            string_amount=str(offer_summary.price_with_optional_parts.amount),
            currency=currency,
        ).protobuf()

        return models_pb2.Offer(
            id=string.uuid(),
            rail=models_pb2.RailOffer(
                cabin_class=[
                    models_pb2.CabinDetails(
                        result_id=detail_id,
                        cabin_class=legacy_models_pb2.CabinClass(
                            type=await self._cabin_mapping.resolve_cabin_class(
                                comfort_class_value,
                                "benerail",
                            ),
                            marketing_name=comfort_class_name,
                        ),
                    )
                    for detail_id in detail_ids
                ],
            ),
            price=price_proto,
            price_breakdown=[
                models_pb2.PriceBreakdown(
                    price=price_proto,
                    breakdown_type=models_pb2.PriceBreakdown.BreakdownType.BREAKDOWN_TYPE_BASE_FARE,
                ),
            ],
        )
