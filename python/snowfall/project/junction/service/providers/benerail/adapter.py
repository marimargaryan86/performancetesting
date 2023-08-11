from __future__ import annotations

import asyncio
import dataclasses
import datetime
from collections.abc import AsyncIterator, Mapping, Sequence

import more_itertools

from snowfall.project.junction.go.service.offers.v1 import (
    models_pb2 as offer_models_pb2,
)
from snowfall.project.junction.go.v1 import models_pb2
from snowfall.project.junction.provider import cabin_classes
from snowfall.project.junction.provider import notifications as base_notifications
from snowfall.project.junction.service.providers.benerail import (
    cache,
    criteria,
    helper_functions,
    train_stations,
)
from snowfall.stdlib import money, string
from snowfall.stdlib.format import protobuf
from snowfall.stdlib.transport.amqp import producer
from snowfall.stdlib.transport.http import errors
from snowfall.stdlib.v1 import latlng_pb2
from snowfall.vendor.benerail import client
from snowfall.vendor.benerail.models import link as models_link
from snowfall.vendor.benerail.models import types
from snowfall.vendor.benerail.models.dialogue import dialogue, passenger
from snowfall.vendor.benerail.models.trip_offers import link
from snowfall.vendor.benerail.models.trip_offers import response as trip_offer_response
from snowfall.vendor.benerail.models.trips import response as trips_response
from snowfall.vendor.benerail.models.trips import trips


class BenerailError(Exception):
    """Raised when there is an exception in the Benerail adapter."""


_NON_BOOKABLE_STATES = frozenset(("NOT_BOOKABLE_NO_SERVICE", "NOT_BOOKABLE_NO_PAST"))
_DATE_FMT = "%Y%m%d"
_FIRST_CLASS_COMFORT_TYPES = frozenset(
    (
        "urn:bdws:class:1",
        "urn:rtb:class:1",
        "urn:itti:class:1",
        "urn:csta:class:1",
        "urn:ama:class:001",
        "urn:bnds:class:1",
        "urn:awdi:class:001",
        "urn:epa:class:1",
        "urn:htrl:class:1",
        "urn:uic:class:1",
        "urn:taco:class:1",
        "urn:trl:class:first",
        "urn:pao:class:1",
    ),
)


@dataclasses.dataclass(frozen=True)
class _CreatePassengersResponse(object):
    passenger_ids: list[str]
    dialogue_etag: str
    passenger_etags: dict[str, str] = dataclasses.field(default_factory=dict)


@dataclasses.dataclass(frozen=True)
class _CreateTripFilterResponse(object):
    trip_filter_id: str
    dialogue_etag: str


@dataclasses.dataclass(frozen=True)
class _DialogueInfo(object):
    dialogue_id: str
    dialogue_etag: str


class NextPageUrlNotFoundError(ValueError):
    """Raised when a sequence of links doesn't contain the next page reference."""


def _next_page_id(links: Sequence[models_link.Link]) -> str:
    for link_obj in links:
        if link_obj.title == "next":
            return helper_functions.last_id_of_url(link_obj.href)

    raise NextPageUrlNotFoundError


class BenerailAdapter(object):  # noqa: WPS214
    def __init__(  # noqa: WPS211
        self,
        benerail_client: client.BenerailClient,
        train_station_repository: train_stations.TrainStationRepository,
        offers_cache: cache.OffersCache,
        ttl: datetime.timedelta,
        notifier: base_notifications.Notifier,
        provider_cabin_class_mapping: cabin_classes.CabinMappingRepository,
        notifications_producer: producer.Producer,
    ) -> None:
        self._train_stations = train_station_repository
        self._cabin_mapping = provider_cabin_class_mapping
        self._client = benerail_client
        self._offers_cache = offers_cache
        self._ttl = ttl
        self._notifier = notifier
        self._notifications_producer = notifications_producer

    async def gather_search_results(  # noqa: WPS210
        self,
        search_task: criteria.SearchCriteria,
    ) -> AsyncIterator[offer_models_pb2.OfferGroup]:
        dialogue_res = await self._client.dialogue.create_dialogue(
            session_token=search_task.br_session_token,
        )
        dialogue_id = dialogue_res.response_result.identifier

        create_passenger_res = await self._create_passengers(
            dialogue_info=_DialogueInfo(
                dialogue_id=dialogue_id,
                dialogue_etag=dialogue_res.etag,
            ),
            passenger_dobs=search_task.passenger_dobs,
            session_token=search_task.br_session_token,
        )
        create_trip_filter_res = await self._create_trip_filter(
            dialogue_info=_DialogueInfo(
                dialogue_id=dialogue_id,
                dialogue_etag=create_passenger_res.dialogue_etag,
            ),
            origin=search_task.origin,
            destination=search_task.destination,
            departure_datetime=search_task.outbound_departure_datetime,
            session_token=search_task.br_session_token,
        )

        offer_group_iterator = self._get_offer_groups(
            dialogue_info=_DialogueInfo(
                dialogue_id=dialogue_id,
                dialogue_etag=create_trip_filter_res.dialogue_etag,
            ),
            trip_filter_id=create_trip_filter_res.trip_filter_id,
            passenger_ids=create_passenger_res.passenger_ids,
            passenger_etags=create_passenger_res.passenger_etags,
            departure_after=search_task.outbound_departure_datetime,
            session_token=search_task.br_session_token,
        )

        async for offer in offer_group_iterator:
            yield offer

    async def _create_passengers(
        self,
        dialogue_info: _DialogueInfo,
        passenger_dobs: Sequence[datetime.date],
        session_token: str | None = None,
    ) -> _CreatePassengersResponse:
        passenger_ids = []
        passenger_etags = {}
        etag = dialogue_info.dialogue_etag

        for date_of_birth in passenger_dobs:
            passenger_res = await self._client.passengers_client.create_passenger(
                dialogue_id=dialogue_info.dialogue_id,
                etag=etag,
                body=passenger.PassengerRequest(
                    date_of_birth=date_of_birth,
                ),
                session_token=session_token,
            )
            etag = passenger_res.etag
            passenger_ids.append(passenger_res.response_result.identifier)
            passenger_etags[passenger_res.response_result.identifier] = (
                passenger_res.metadata.resource_etag or ""
            )

        return _CreatePassengersResponse(
            passenger_ids=passenger_ids,
            dialogue_etag=etag,
            passenger_etags=passenger_etags,
        )

    async def _create_trip_filter(  # noqa: WPS211
        self,
        dialogue_info: _DialogueInfo,
        origin: str,
        destination: str,
        departure_datetime: datetime.datetime,
        session_token: str | None = None,
    ) -> _CreateTripFilterResponse:
        trip_filter_res = await self._client.trip_filter.create_trip_filter(
            dialogue_id=dialogue_info.dialogue_id,
            etag=dialogue_info.dialogue_etag,
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

    async def _get_offer_groups(  # noqa: WPS210, WPS211
        self,
        dialogue_info: _DialogueInfo,
        trip_filter_id: str,
        passenger_ids: Sequence[str],
        passenger_etags: Mapping[str, str],
        departure_after: datetime.datetime,
        session_token: str | None = None,
    ) -> AsyncIterator[offer_models_pb2.OfferGroup]:
        trip_offer_filter = (
            await self._client.trip_offer_filter_client.create_trip_offer_filter(
                dialogue_id=dialogue_info.dialogue_id,
                etag=dialogue_info.dialogue_etag,
                body=dialogue.DialogueIdTripofferfiltersBody(
                    trip_filter_id=trip_filter_id,
                    passengers=list(passenger_ids),
                ),
                session_token=session_token,
            )
        )

        trip_offers_iterator = self._get_trips_of_offer_collection(
            collection_id=trip_offer_filter.response_result.identifier,
            departure_after=departure_after,
            session_token=session_token,
        )

        trip_offer_ids = [
            helper_functions.last_id_of_url(trip_offer.href)
            async for trip_offer in trip_offers_iterator
        ]

        if not trip_offer_ids:
            return

        offer_info_responses = await self._get_offer_info_responses(
            trip_offer_ids=trip_offer_ids,
            session_token=session_token,
        )
        trip_info_responses = await self._get_trip_info_responses(
            offer_info_responses=offer_info_responses,
            session_token=session_token,
        )

        expires_at_dt = datetime.datetime.now(datetime.UTC) + self._ttl

        for idx, offer_info_response in enumerate(offer_info_responses):
            segment_id = string.uuid()

            yield offer_models_pb2.OfferGroup(
                id=string.uuid(),
                expires_at=protobuf.datetime_to_protobuf(expires_at_dt),
                offers=[
                    await self._parse_offer(
                        offer_res=offer_info_response,
                        expires_at=expires_at_dt,
                        trip_info=trip_info_responses[idx],
                        offer_segment_id=segment_id,
                        passenger_etags=passenger_etags,
                        dialogue_id=dialogue_info.dialogue_id,
                        session_token=session_token,
                    ),
                ],
                segments=[
                    self._parse_segment_info(
                        trip_info=trip_info_responses[idx],
                        segment_id=segment_id,
                    ),
                ],
            )

    async def _get_trips_of_offer_collection(  # noqa: WPS231
        self,
        collection_id: str,
        departure_after: datetime.datetime,
        session_token: str | None = None,
    ) -> AsyncIterator[link.TripOfferResourceLink]:
        get_coll = self._client.trip_offers_client.get_trip_offer_ids_in_collection
        collection = await get_coll(
            trip_offer_collection_id=collection_id,
            session_token=session_token,
        )

        while collection.response_result.trip_offers:
            for trip_offer in collection.response_result.trip_offers:
                if departure_after.date().strftime(_DATE_FMT) not in trip_offer.title:
                    return

                summary = trip_offer.summary

                if summary is None:
                    continue

                if summary.bookable_status.status_value not in _NON_BOOKABLE_STATES:
                    yield trip_offer

            try:
                collection = await get_coll(
                    trip_offer_collection_id=_next_page_id(collection.links),
                    session_token=session_token,
                )
            except (StopIteration, errors.HttpError):
                return

    def _parse_segment_info(
        self,
        trip_info: trips_response.GetTripResponse,
        segment_id: str,
    ) -> offer_models_pb2.OfferSegment:
        number = ""

        for leg in trip_info.response_result.trip_legs:
            if isinstance(leg, trips.TimedLeg) and leg.train_numbers:
                if leg.train_numbers:
                    number = more_itertools.first(leg.train_numbers)
                else:
                    break

        return offer_models_pb2.OfferSegment(
            id=segment_id,
            legs=self._parse_leg_info(trip_info),
            vehicle=offer_models_pb2.Vehicle(
                number=number,
            ),
            type=models_pb2.Schedule.TYPE_RAIL,
        )

    def _parse_leg_info(
        self,
        trip_info: trips_response.GetTripResponse,
    ) -> list[offer_models_pb2.OfferSegmentLeg]:
        legs = []

        for leg_info in trip_info.response_result.trip_legs:
            if not isinstance(leg_info, trips.TimedLeg):
                continue

            origin = self._train_stations.resolve_place_with_urn(
                leg_info.origin.place_value,
            )
            destination = self._train_stations.resolve_place_with_urn(
                leg_info.destination.place_value,
            )

            legs.append(
                offer_models_pb2.OfferSegmentLeg(
                    id=string.uuid(),
                    origin=models_pb2.Point(
                        ref=origin.identifier,
                        name=origin.name or "",
                        coordinates=latlng_pb2.LatLng(
                            latitude=origin.latitude,
                            longitude=origin.longitude,
                        ),
                        time_zone=origin.timezone.key,
                    ),
                    destination=models_pb2.Point(
                        ref=destination.identifier,
                        name=destination.name or "",
                        coordinates=latlng_pb2.LatLng(
                            latitude=destination.latitude,
                            longitude=destination.longitude,
                        ),
                        time_zone=origin.timezone.key,
                    ),
                    departure_at=(
                        protobuf.datetime_to_protobuf(
                            datetime.datetime.strptime(
                                leg_info.departure_at,
                                "%Y-%m-%dT%H:%M:%S%z",
                            ),
                        )
                    ),
                    arrival_at=(
                        protobuf.datetime_to_protobuf(
                            datetime.datetime.strptime(
                                leg_info.arrival_at,
                                "%Y-%m-%dT%H:%M:%S%z",
                            ),
                        )
                    ),
                ),
            )

        return legs

    async def _parse_offer(  # noqa: WPS211
        self,
        offer_res: trip_offer_response.GetOfferResponse,
        expires_at: datetime.datetime,
        trip_info: trips_response.GetTripResponse,
        offer_segment_id: str,
        dialogue_id: str,
        passenger_etags: Mapping[str, str],
        session_token: str | None = None,
    ) -> offer_models_pb2.Offer:
        cabin_class_type = models_pb2.CabinClass.TYPE_ECONOMY
        comfort_class_value = (
            str(
                offer_res.response_result.comfort_class.comfort_class_value,
            )
            if offer_res.response_result.comfort_class
            else ""
        )

        if comfort_class_value in _FIRST_CLASS_COMFORT_TYPES:
            cabin_class_type = models_pb2.CabinClass.TYPE_FIRST

        price_proto = money.from_string(
            string_amount=str(offer_res.response_result.price.amount),
            currency=money.Currency(
                offer_res.response_result.price.currency.upper(),
            ),
        ).protobuf()

        return offer_models_pb2.Offer(
            id=await self._offers_cache.store(
                cache.OfferDetails(
                    offer_id=offer_res.response_result.identifier,
                    price=str(offer_res.response_result.price.amount),
                    currency=money.Currency(
                        offer_res.response_result.price.currency.upper(),
                    ),
                    dialogue_id=dialogue_id,
                    session_token=session_token,
                    passenger_etags=passenger_etags,
                    departure_at=trip_info.response_result.departure_at,
                ),
                expires_at=expires_at,
            ),
            segment_details=[
                offer_models_pb2.OfferSegmentDetails(
                    id=string.uuid(),
                    offer_segment_id=offer_segment_id,
                    cabin_class=models_pb2.CabinClass(
                        type=cabin_class_type,
                        marketing_name=(
                            str(
                                offer_res.response_result.comfort_class.comfort_class_value,
                            )
                            if offer_res.response_result.comfort_class is not None
                            else ""
                        ),
                    ),
                ),
            ],
            price=price_proto,
            price_breakdown=[
                offer_models_pb2.PriceBreakdown(
                    price=price_proto,
                    breakdown_type=offer_models_pb2.PriceBreakdown.BreakdownType.BREAKDOWN_TYPE_BASE_FARE,
                ),
            ],
            brand_name=(
                str(
                    offer_res.response_result.comfort_class.comfort_class_value,
                )
                if offer_res.response_result.comfort_class is not None
                else ""
            ),
        )

    async def _get_offer_info_responses(
        self,
        trip_offer_ids: Sequence[str],
        session_token: str | None = None,
    ) -> list[trip_offer_response.GetOfferResponse]:
        trip_offers_responses = await asyncio.gather(
            *(
                self._client.trip_offers_client.get_trip_offer_info(
                    trip_offer_id=trip_offer_id,
                    session_token=session_token,
                )
                for trip_offer_id in trip_offer_ids
            ),
        )

        return await asyncio.gather(
            *(
                self._client.offers_client.get_offer_info(
                    helper_functions.last_id_of_url(offer_link.href),
                    session_token,
                )
                for trip_offers_response in trip_offers_responses
                for offer_link in trip_offers_response.response_result.offers
            ),
        )

    async def _get_trip_info_responses(
        self,
        offer_info_responses: Sequence[trip_offer_response.GetOfferResponse],
        session_token: str | None = None,
    ) -> list[trips_response.GetTripResponse]:
        get_trip_info_coroutines = []

        for offer_info_response in offer_info_responses:
            href = offer_info_response.response_result.trip.href

            get_trip_info_coroutines.append(
                self._client.trips_client.get_trip_info(
                    trip_id=helper_functions.last_id_of_url(href),
                    session_token=session_token,
                ),
            )

        return await asyncio.gather(*get_trip_info_coroutines)
