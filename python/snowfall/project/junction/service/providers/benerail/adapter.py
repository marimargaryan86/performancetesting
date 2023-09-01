from __future__ import annotations

import asyncio
import dataclasses
import datetime
import types as std_types
from collections.abc import AsyncIterator, Iterable, Mapping, Sequence
from gettext import gettext as _

import asyncstdlib
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
    helper_models,
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
from snowfall.vendor.benerail.models.trip_offers import link, offer
from snowfall.vendor.benerail.models.trip_offers import response as trip_offer_response
from snowfall.vendor.benerail.models.trips import trips


class BenerailError(Exception):
    """Raised when there is an exception in the Benerail adapter."""


_NON_BOOKABLE_STATES = frozenset(("NOT_BOOKABLE_NO_SERVICE", "NOT_BOOKABLE_NO_PAST"))
_DATE_FMT = "%Y%m%d"
_FLEXIBILITY_NAMES = std_types.MappingProxyType(
    {
        "FF": _("Full flex"),
        "MF": _("Mid flex"),
        "NF": _("Non flex"),
    },
)
_FLEX_NA = _("Flex info N/A")


@dataclasses.dataclass(frozen=True)
class _CreatePassengersResponse(object):
    dialogue_etag: str
    passengers_info: list[helper_models.PassengerInfo]


@dataclasses.dataclass(frozen=True)
class _CreateTripFilterResponse(object):
    trip_filter_id: str
    dialogue_etag: str


class NextPageUrlNotFoundError(ValueError):
    """Raised when a sequence of links doesn't contain the next page reference."""


def _next_page_id(links: Sequence[models_link.Link]) -> str:
    for link_obj in links:
        if link_obj.title == "next":
            return helper_functions.last_id_of_url(link_obj.href)

    raise NextPageUrlNotFoundError


def _get_brand_name(comfort_class_name: str, flexibility_value: str) -> str:
    return "{0} / {1}".format(
        comfort_class_name,
        _FLEXIBILITY_NAMES.get(flexibility_value[-2:], _FLEX_NA),
    ).strip(" /")


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
            dialogue_info=helper_models.DialogueInfo(
                identifier=dialogue_id,
                etag=dialogue_res.etag,
            ),
            passenger_dobs=search_task.passenger_dobs,
            session_token=search_task.br_session_token,
        )
        create_trip_filter_res = await self._create_trip_filter(
            dialogue_info=helper_models.DialogueInfo(
                identifier=dialogue_id,
                etag=create_passenger_res.dialogue_etag,
            ),
            origin=search_task.origin,
            destination=search_task.destination,
            departure_datetime=search_task.outbound_departure_datetime,
            session_token=search_task.br_session_token,
        )

        offer_group_iterator = self._get_offer_groups(
            dialogue_info=helper_models.DialogueInfo(
                identifier=dialogue_id,
                etag=create_trip_filter_res.dialogue_etag,
            ),
            trip_filter_id=create_trip_filter_res.trip_filter_id,
            passengers_info=create_passenger_res.passengers_info,
            departure_after=search_task.outbound_departure_datetime,
            session_token=search_task.br_session_token,
        )

        async for offer_group in offer_group_iterator:
            yield offer_group

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

    async def _create_trip_filter(  # noqa: WPS211
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

    async def _get_offer_groups(  # noqa: WPS210, WPS211
        self,
        dialogue_info: helper_models.DialogueInfo,
        trip_filter_id: str,
        passengers_info: Sequence[helper_models.PassengerInfo],
        departure_after: datetime.datetime,
        session_token: str | None = None,
    ) -> AsyncIterator[offer_models_pb2.OfferGroup]:
        trip_offer_filter = (
            await self._client.trip_offer_filter_client.create_trip_offer_filter(
                dialogue_id=dialogue_info.identifier,
                etag=dialogue_info.etag,
                body=dialogue.DialogueIdTripofferfiltersBody(
                    trip_filter_id=trip_filter_id,
                    passengers=[pax_info.identifier for pax_info in passengers_info],
                ),
                session_token=session_token,
            )
        )
        dialogue_info = helper_models.DialogueInfo(
            identifier=dialogue_info.identifier,
            etag=trip_offer_filter.etag,
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

        trip_offer_responses_iterator = self._get_trip_offers(
            trip_offer_ids=trip_offer_ids,
            session_token=session_token,
        )

        trip_offer_responses = [
            trip_offer_res
            for trip_offer_res in await trip_offer_responses_iterator
            if trip_offer_res.response_result.offers
        ]
        trip_id_offer_ids = tuple(
            (
                helper_functions.last_id_of_url(
                    trip_offer_response.response_result.trip.href,
                ),
                tuple(
                    helper_functions.last_id_of_url(offer_link.href)
                    for offer_link in trip_offer_response.response_result.offers
                ),
            )
            for trip_offer_response in trip_offer_responses
        )

        offer_map = await self._get_offer_map(
            offer_ids=(
                offer_id for _, offer_ids in trip_id_offer_ids for offer_id in offer_ids
            ),
            session_token=session_token,
        )

        trip_map = await self._get_trip_map(
            trip_ids=(trip_id for trip_id, _ in trip_id_offer_ids),
            session_token=session_token,
        )

        expires_at_dt = datetime.datetime.now(datetime.UTC) + self._ttl

        for trip_id, offer_ids in trip_id_offer_ids:
            segment_id = string.uuid()
            offers = [
                await self._parse_offer(
                    offer_obj=offer_map[offer_id],
                    expires_at=expires_at_dt,
                    trip=trip_map[trip_id],
                    offer_segment_id=segment_id,
                    passengers_info=passengers_info,
                    dialogue_info=dialogue_info,
                    session_token=session_token,
                )
                for offer_id in offer_ids
            ]

            yield offer_models_pb2.OfferGroup(
                id=string.uuid(),
                expires_at=protobuf.datetime_to_protobuf(expires_at_dt),
                offers=offers,
                segments=[
                    self._parse_segment_info(
                        trip=trip_map[trip_id],
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
        trip: trips.Trip,
        segment_id: str,
    ) -> offer_models_pb2.OfferSegment:
        number = ""

        for leg in trip.trip_legs:
            if isinstance(leg, trips.TimedLeg) and leg.train_numbers:
                if leg.train_numbers:
                    number = more_itertools.first(leg.train_numbers)
                else:
                    break

        return offer_models_pb2.OfferSegment(
            id=segment_id,
            legs=self._parse_leg_info(trip),
            vehicle=offer_models_pb2.Vehicle(
                number=number,
            ),
            type=models_pb2.Schedule.TYPE_RAIL,
        )

    def _parse_leg_info(
        self,
        trip: trips.Trip,
    ) -> list[offer_models_pb2.OfferSegmentLeg]:
        legs = []

        for leg_info in trip.trip_legs:
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
        offer_obj: offer.Offer,
        expires_at: datetime.datetime,
        trip: trips.Trip,
        offer_segment_id: str,
        dialogue_info: helper_models.DialogueInfo,
        passengers_info: Sequence[helper_models.PassengerInfo],
        session_token: str | None = None,
    ) -> offer_models_pb2.Offer:
        comfort_class_value = (
            str(
                offer_obj.comfort_class.comfort_class_value,
            )
            if offer_obj.comfort_class
            else ""
        )

        price_proto = money.from_string(
            string_amount=str(offer_obj.price.amount),
            currency=money.Currency(
                offer_obj.price.currency.upper(),
            ),
        ).protobuf()
        comfort_class_name = (
            await self._resolve_marketing_name(comfort_class_value)
            if comfort_class_value
            else ""
        )

        return offer_models_pb2.Offer(
            id=await self._offers_cache.store(
                cache.OfferDetails(
                    offer_id=offer_obj.identifier,
                    price=str(offer_obj.price.amount),
                    currency=money.Currency(
                        offer_obj.price.currency.upper(),
                    ),
                    dialogue_info=dialogue_info,
                    session_token=session_token,
                    passengers_info=passengers_info,
                    departure_at=trip.departure_at,
                ),
                expires_at=expires_at,
            ),
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
                ),
            ],
            price=price_proto,
            price_breakdown=[
                offer_models_pb2.PriceBreakdown(
                    price=price_proto,
                    breakdown_type=offer_models_pb2.PriceBreakdown.BreakdownType.BREAKDOWN_TYPE_BASE_FARE,
                ),
            ],
            brand_name=_get_brand_name(
                comfort_class_name=comfort_class_name,
                flexibility_value=offer_obj.flexibility.flexibility_value,
            ),
        )

    @asyncstdlib.lru_cache()
    async def _resolve_marketing_name(self, comfort_class_value: str) -> str:
        try:
            urn_val = await self._client.rcode_client.get_urn_value(comfort_class_value)
        except errors.HttpError:
            return comfort_class_value

        try:
            rcode = urn_val.response_result.rcodes[0]
        except (IndexError, ValueError):
            return comfort_class_value

        try:
            en_label = rcode.labels["en"]
        except KeyError:
            return comfort_class_value

        return en_label.code_long or comfort_class_value

    async def _get_trip_offers(
        self,
        trip_offer_ids: Sequence[str],
        session_token: str | None = None,
    ) -> list[trip_offer_response.GetTripOfferResponse]:
        return await asyncio.gather(
            *(
                self._client.trip_offers_client.get_trip_offer_info(
                    trip_offer_id=trip_offer_id,
                    session_token=session_token,
                )
                for trip_offer_id in trip_offer_ids
            ),
        )

    async def _get_offer_map(
        self,
        offer_ids: Iterable[str],
        session_token: str | None = None,
    ) -> Mapping[str, offer.Offer]:
        gathered_coros = asyncio.gather(
            *(
                self._client.offers_client.get_offer_info(
                    offer_id,
                    session_token,
                )
                for offer_id in offer_ids
            ),
        )

        return {
            res.response_result.identifier: res.response_result
            for res in await gathered_coros
        }

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

        return {
            trip_res.response_result.identifier: trip_res.response_result
            for trip_res in await asyncio.gather(*get_trip_coroutines)
        }
