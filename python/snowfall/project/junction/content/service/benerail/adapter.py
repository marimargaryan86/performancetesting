import asyncio
import dataclasses
import datetime
from collections.abc import AsyncIterator, Awaitable, Callable, Mapping, Sequence
from typing import Any

import tenacity

from snowfall.stdlib.logging import stdout
from snowfall.stdlib.transport.http import errors
from snowfall.vendor.benerail import client
from snowfall.vendor.benerail.models import types
from snowfall.vendor.benerail.models.dialogue import dialogue, passenger
from snowfall.vendor.benerail.models.trip_offers import (
    offer as trip_offers_offer,
)
from snowfall.vendor.benerail.models.trip_offers import (
    response as trip_offers_response,
)
from snowfall.vendor.benerail.models.trip_offers import (
    trip_offers as trip_offers_trip_offers,
)
from snowfall.vendor.benerail.models.trips import trips

_NON_BOOKABLE_STATES = frozenset(("NOT_BOOKABLE_NO_SERVICE", "NOT_BOOKABLE_NO_PAST"))
_BENERAIL_PUBLIC_FARES_CODE = "urn:bnds:market_segment_preference:REQ_PUBLIC"
_logger = stdout.get_logger()


@dataclasses.dataclass(frozen=True)
class _PassengerInfo:
    identifier: str
    etag: str
    date_of_birth: datetime.date


@dataclasses.dataclass(frozen=True)
class _DialogueInfo:
    identifier: str
    etag: str


@dataclasses.dataclass(frozen=True)
class _CreatePassengersResponse:
    dialogue_etag: str
    passengers_info: Sequence[_PassengerInfo]


@dataclasses.dataclass(frozen=True)
class _CreateTripFilterResponse:
    trip_filter_id: str
    dialogue_etag: str


@dataclasses.dataclass(frozen=True)
class _TripData:
    dialogue_id: str
    dialogue_etag: str
    create_passengers_response: _CreatePassengersResponse
    create_trip_filter_response: _CreateTripFilterResponse


@dataclasses.dataclass(frozen=True)
class _TripDataCriterion:
    origin: str
    destination: str
    departure_datetime: datetime.datetime
    passenger_dobs: Sequence[datetime.date]
    session_token: str | None = None


@dataclasses.dataclass(frozen=True)
class _TripOfferResponsesWithPassengers:
    passengers_info: Sequence[_PassengerInfo]
    trip_offer_responses: Sequence[trip_offers_response.GetTripOfferResponse]
    dialogue_info: _DialogueInfo


@dataclasses.dataclass(frozen=True)
class _TripOfferResponsesWithPassengersCriterion:
    origin: str
    destination: str
    outbound_departure_datetime: datetime.datetime
    passenger_dobs: Sequence[datetime.date]
    session_token: str | None = None


@dataclasses.dataclass(frozen=True)
class GetOfferResponse:
    offer: trip_offers_offer.Offer
    dialogue_info: _DialogueInfo
    passengers_info: Sequence[_PassengerInfo]
    departure_at: str


@dataclasses.dataclass(frozen=True)
class TripWithOffers:
    trip: trips.Trip
    offers: list[trip_offers_offer.Offer]


@dataclasses.dataclass(frozen=True)
class TripWithTripOffer:
    trip: trips.Trip
    trip_offer: trip_offers_trip_offers.TripOffer


_CHUNK_SIZE = 10


async def _request_by_chunks(
    function_obj: Callable[..., Awaitable[Any]],
    argument_mappings: Sequence[Mapping[str, Any]],
) -> AsyncIterator[Any]:
    for index in range(0, len(argument_mappings), _CHUNK_SIZE):
        responses = await asyncio.gather(
            *(
                tenacity.retry(
                    retry=tenacity.retry_if_exception_type(errors.HttpError),
                    wait=tenacity.wait_fixed(1),
                    stop=tenacity.stop_after_attempt(3),
                )(function_obj)(**arguments)
                for arguments in argument_mappings[index : index + _CHUNK_SIZE]
            ),
            return_exceptions=True,
        )

        for response in responses:
            if isinstance(response, tenacity.RetryError):
                _logger.error(
                    "Request failed",
                    exc_info=(
                        type(response),
                        response,
                        response.__traceback__,
                    ),
                    last_attempt=str(response.last_attempt),
                )
            else:
                yield response


class BenerailAdapter:
    def __init__(self, benerail_client: client.BenerailClient) -> None:
        self._client = benerail_client

    async def search_with_offers(
        self,
        origin: str,
        destination: str,
        departure_datetime: datetime.datetime,
        passenger_dobs: Sequence[datetime.date],
        session_token: str,
    ) -> AsyncIterator[TripWithOffers]:
        trip_trip_offer_iterator = self.search_with_trip_offers(
            origin=origin,
            destination=destination,
            departure_datetime=departure_datetime,
            passenger_dobs=passenger_dobs,
            session_token=session_token,
        )

        trip_trip_offer_objects = [
            trip_trip_offer_obj
            async for trip_trip_offer_obj in trip_trip_offer_iterator
        ]

        offers_iterator = _request_by_chunks(
            self._get_offers,
            tuple(
                {
                    "offer_ids": tuple(
                        offer.identifier
                        for offer in trip_trip_offer_object.trip_offer.offers
                    ),
                    "session_token": session_token,
                }
                for trip_trip_offer_object in trip_trip_offer_objects
            ),
        )

        offer_map = {
            offer_info_obj.identifier: offer_info_obj
            async for offer_info in offers_iterator
            for offer_info_obj in offer_info
        }

        for trip_trip_offer_object in trip_trip_offer_objects:
            trip = trip_trip_offer_object.trip
            offers = trip_trip_offer_object.trip_offer.offers

            yield TripWithOffers(
                trip=trip,
                offers=[offer_map[offer.identifier] for offer in offers],
            )

    async def search_with_trip_offers(
        self,
        origin: str,
        destination: str,
        departure_datetime: datetime.datetime,
        passenger_dobs: Sequence[datetime.date],
        session_token: str,
    ) -> AsyncIterator[TripWithTripOffer]:
        trip_offer_responses_with_passengers = (
            await self._get_trip_offer_responses_with_passengers(
                criterion=_TripOfferResponsesWithPassengersCriterion(
                    origin=origin,
                    destination=destination,
                    outbound_departure_datetime=departure_datetime,
                    passenger_dobs=passenger_dobs,
                    session_token=session_token,
                ),
            )
        )
        trip_offer_responses = trip_offer_responses_with_passengers.trip_offer_responses
        passengers_info = trip_offer_responses_with_passengers.passengers_info

        if not trip_offer_responses or not passengers_info:
            return

        trip_map = await self._get_trip_map(
            trip_ids=tuple(
                trip_offer_res.response_result.trip.identifier
                for trip_offer_res in trip_offer_responses
            ),
            session_token=session_token,
        )

        for trip_offer_response in trip_offer_responses:
            try:
                trip = trip_map[trip_offer_response.response_result.trip.identifier]
            except KeyError:
                _logger.warning(
                    "Trip info not found, skipping trip offer",
                    trip_offer_response=trip_offer_response,
                )

                continue

            yield TripWithTripOffer(
                trip=trip,
                trip_offer=trip_offer_response.response_result,
            )

    async def _create_passengers(
        self,
        dialogue_info: _DialogueInfo,
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
                _PassengerInfo(
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
        dialogue_info: _DialogueInfo,
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

    async def _dialogue_with_passengers_and_trip_filter(
        self,
        criterion: _TripDataCriterion,
    ) -> _TripData:
        dialogue_res = await self._client.dialogue.create_dialogue(
            session_token=criterion.session_token,
        )
        dialogue_id = dialogue_res.response_result.identifier

        create_passenger_res = await self._create_passengers(
            dialogue_info=_DialogueInfo(
                identifier=dialogue_id,
                etag=dialogue_res.etag,
            ),
            passenger_dobs=criterion.passenger_dobs,
            session_token=criterion.session_token,
        )
        create_trip_filter_res = await self._create_trip_filter(
            dialogue_info=_DialogueInfo(
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

    async def _get_trip_offers(
        self,
        trip_offer_ids: Sequence[str],
        session_token: str | None = None,
    ) -> Sequence[trip_offers_response.GetTripOfferResponse]:
        response_iterator = _request_by_chunks(
            self._client.trip_offers_client.get_trip_offer_info,
            tuple(
                {
                    "trip_offer_id": trip_offer_id,
                    "session_token": session_token,
                }
                for trip_offer_id in trip_offer_ids
            ),
        )

        return [response async for response in response_iterator]

    async def _get_trip_offer_responses_with_passengers(  # noqa: WPS231
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
                market_segment=dialogue.MarketSegment(code=_BENERAIL_PUBLIC_FARES_CODE),
            ),
            session_token=criterion.session_token,
        )

        get_coll = self._client.trip_offers_client.get_trip_offer_ids_in_collection

        # get previous and next collections through the day, starts from noon
        collections = [
            await get_coll(
                trip_offer_collection_id=trip_offer_filter.response_result.identifier,
                session_token=criterion.session_token,
            ),
        ]
        previous_collection = collections[0]
        next_collection = collections[0]

        for idx in range(6):
            collection_ids = [
                next(
                    link.identifier
                    for link in previous_collection.links
                    if link.title == "previous"
                ),
            ]

            if idx < 5:
                collection_ids.append(
                    next(
                        link.identifier
                        for link in next_collection.links
                        if link.title == "next"
                    ),
                )

            collections.extend(
                await self._get_collections(
                    collections_ids=collection_ids,
                    session_token=criterion.session_token,
                ),
            )

            previous_collection = collections[0]

            if len(collections) == 2:
                next_collection = collections[1]

        trip_offer_ids = []
        for collection in collections:
            if not collection.response_result.trip_offers:
                continue

            for trip_offer in collection.response_result.trip_offers:
                summary = trip_offer.summary

                if summary is None:
                    continue

                if summary.bookable_status.status_value not in _NON_BOOKABLE_STATES:
                    trip_offer_ids.append(trip_offer.identifier)

        dialogue_info = _DialogueInfo(
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

        trip_offer_responses = sorted(
            (
                response
                for response in await trip_offer_responses_iterator
                if response.response_result.offers
            ),
            key=lambda response: datetime.datetime.fromisoformat(
                response.response_result.departure_at,
            ),
        )

        return _TripOfferResponsesWithPassengers(
            trip_offer_responses=trip_offer_responses,
            passengers_info=(
                trip_filter_creation.create_passengers_response.passengers_info
            ),
            dialogue_info=dialogue_info,
        )

    async def _get_collections(
        self,
        collections_ids: Sequence[str],
        session_token: str | None = None,
    ) -> Sequence[trip_offers_response.GetTripOfferCollectionResponse]:
        get_coll = self._client.trip_offers_client.get_trip_offer_ids_in_collection

        return await asyncio.gather(
            *(
                get_coll(
                    trip_offer_collection_id=collection_id,
                    session_token=session_token,
                )
                for collection_id in collections_ids
            ),
        )

    async def _get_offers(
        self,
        offer_ids: Sequence[str],
        session_token: str | None = None,
    ) -> Sequence[trip_offers_offer.Offer]:
        responses = await asyncio.gather(
            *(
                self._client.offers_client.get_offer_info(
                    offer_id,
                    session_token,
                )
                for offer_id in offer_ids
            ),
        )

        return [
            response.response_result
            for response in responses
            if response.response_result.price.currency != "?"
        ]

    async def _get_trip_map(
        self,
        trip_ids: Sequence[str],
        session_token: str | None = None,
    ) -> Mapping[str, trips.Trip]:
        get_trip_iterator = _request_by_chunks(
            self._client.trips_client.get_trip,
            tuple(
                {"trip_id": trip_id, "session_token": session_token}
                for trip_id in trip_ids
            ),
        )

        trip_map = {}

        async for get_trip_response in get_trip_iterator:
            trip_map[get_trip_response.response_result.identifier] = (
                get_trip_response.response_result
            )

        return trip_map
