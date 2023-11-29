import asyncio
import datetime
import functools
import math
import pathlib
from collections.abc import AsyncIterator

from snowfall.project.junction.go.service.offers.v1 import (
    amqp_pb2 as offers_amqp_pb2,
)
from snowfall.project.junction.go.service.offers.v1 import models_pb2 as offers_pb2
from snowfall.project.junction.go.service.orders.v1 import (
    amqp_pb2 as orders_amqp_pb2,
)
from snowfall.project.junction.go.v1 import models_pb2
from snowfall.project.junction.provider import notifications as base_notifications
from snowfall.project.junction.service.providers.benerail import (
    adapter,
    booking,
    cache,
    criteria,
    fare_rules,
    notifications,
    train_stations,
)
from snowfall.project.junction.service.providers.benerail.v1 import (
    amqp_pb2 as br_amqp_pb2,
)
from snowfall.stdlib import h3, money
from snowfall.stdlib.format import protobuf
from snowfall.stdlib.logging import stdout
from snowfall.stdlib.persistence import filesystem
from snowfall.stdlib.transport.amqp import consumer, producer, types
from snowfall.stdlib.transport.http import errors
from snowfall.stdlib.v1 import latlng_pb2
from snowfall.vendor.benerail import client
from snowfall.vendor.benerail.models import etag

_PROVIDER_NAME = "Benerail"
_RETRY_TTL = datetime.timedelta(hours=1)
_RETRY_AFTER_SECONDS = 120


class NotificationsConsumer(object):
    def __init__(
        self,
        consumer_obj: consumer.Consumer[br_amqp_pb2.BookingNotificationTask],
        benerail_client: client.BenerailClient,
        notifier: base_notifications.Notifier,
        booking_storage: filesystem.Storage,
    ):
        self._booking_storage = booking_storage
        self._consumer = consumer_obj
        self._client = benerail_client
        self._notifier = notifier
        self._logger = stdout.get_logger()

    async def consume(self) -> None:
        await self._consumer.consume(self._process_message)

    async def _process_message(  # noqa: WPS217
        self,
        message: types.Message[br_amqp_pb2.BookingNotificationTask],
    ) -> None:
        body = message.body
        etag_data = etag.EtagData()

        try:
            booking_res, _ = await self._client.bookings_client.get_booking(
                booking_id=body.br_booking_id,
                session_token=body.br_session_token,
            )
        except errors.HttpError:
            self._logger.exception("Failed to fetch the booking")

            return await self._handle_no_fulfillment(message)

        booking_res.set_etags(etag_data)

        if not booking_res.response_result.fulfillments:
            return await self._handle_no_fulfillment(message)

        ticket_urls = (
            await self._client.bookings_client.get_ticket_urls_from_fulfillment(
                booking_id=booking_res.response_result.identifier,
                fulfillment_id=booking_res.response_result.fulfillments[0].identifier,
            )
        )

        if not ticket_urls:
            return await self._handle_no_fulfillment(message)

        storage_path = pathlib.Path(booking_res.response_result.identifier)
        raw_data = await self._booking_storage.get(storage_path)
        all_results = booking.RawStorageData.parse_from_storage(raw_data)
        all_results.tickets = list(ticket_urls)

        await self._booking_storage.put(
            storage_path,
            all_results.json().encode(),
        )

        body.MergeFrom(
            br_amqp_pb2.BookingNotificationTask(
                ticket_url=", ".join(ticket_urls),
            ),
        )

        await self._notifier.send(
            notifications.BookingNotification(body),
        )
        return None

    async def _handle_no_fulfillment(
        self,
        message: types.Message[br_amqp_pb2.BookingNotificationTask],
    ) -> None:
        await asyncio.sleep(_RETRY_AFTER_SECONDS)

        created_at = protobuf.protobuf_to_datetime(
            message.body.created_at,
        )
        time_passed = datetime.datetime.now(datetime.UTC) - created_at

        if time_passed > _RETRY_TTL:
            self._logger.error(
                "Ticket retrieval limit reached",
                booking_id=message.body.booking_id,
            )
            await message.nack()
        else:
            await message.requeue()


class PriceQuoteConsumer(object):
    def __init__(
        self,
        consumer_obj: consumer.Consumer[offers_amqp_pb2.TripPriceQuoteTask],
        producer_obj: producer.Producer,
        cache_container: cache.Cache,
        benerail_client: client.BenerailClient,
        benerail_adapter: adapter.BenerailAdapter,
        price_ttl: datetime.timedelta,
        provider_company_id: str,
    ):
        self._offers_cache = cache_container.offers_cache
        self._booking_offers_cache = cache_container.booking_offers_cache

        self._ttl = price_ttl
        self._consumer = consumer_obj
        self._producer = producer_obj
        self._benerail_client = benerail_client
        self._adapter = benerail_adapter
        self._provider_company_id = provider_company_id
        self._logger = stdout.get_logger()

    async def consume(self) -> None:
        await self._consumer.consume(self._process_message)

    async def _process_message(
        self,
        amqp_message: types.Message[offers_amqp_pb2.TripPriceQuoteTask],
    ) -> None:
        offer_details = await self._offers_cache.fetch(amqp_message.body.option_id)

        if not offer_details:
            return

        try:
            get_offer_res = await self._adapter.find_offer(offer_details)
        except adapter.OfferNotFoundError as ex:
            self._logger.exception(
                "Failed to match offer",
                offer_details=offer_details.dict(),
                offers=ex.offers,
                trip_offer_responses=ex.trip_offer_responses,
            )

            return
        except errors.HttpError:
            self._logger.exception(
                "Failed to get offer for quotation",
                offer_details=offer_details.dict(),
            )

            return

        price_quote_price_proto = money.from_string(
            str(get_offer_res.offer_obj.price.amount),
            money.Currency(
                get_offer_res.offer_obj.price.currency.upper(),
            ),
        ).protobuf()

        expires_at = datetime.datetime.now(tz=datetime.UTC) + self._ttl
        price_quote_id = await self._booking_offers_cache.store(
            cache.BookingOfferDetails(
                offer_id=get_offer_res.offer_obj.identifier,
                price=str(get_offer_res.offer_obj.price.amount),
                currency=money.Currency(
                    get_offer_res.offer_obj.price.currency.upper(),
                ),
                dialogue_id=get_offer_res.dialogue_info.identifier,
                passengers_info=get_offer_res.passengers_info,
                departure_at=get_offer_res.departure_at,
                session_token=offer_details.session_token,
            ),
            expires_at,
        )

        await self._producer.publish(
            offers_amqp_pb2.TripPriceQuoteResult(
                price_quote_container_id=amqp_message.body.price_quote_container_id,
                option_id=amqp_message.body.option_id,
                price_quote=offers_pb2.PriceQuote(
                    id=price_quote_id,
                    option_id=amqp_message.body.option_id,
                    expires_at=protobuf.datetime_to_protobuf(expires_at),
                    price=price_quote_price_proto,
                    price_breakdown=[
                        offers_pb2.PriceBreakdown(
                            price=price_quote_price_proto,
                            breakdown_type=offers_pb2.PriceBreakdown.BreakdownType.BREAKDOWN_TYPE_BASE_FARE,
                        ),
                    ],
                    required_documents=[],
                    rules=await fare_rules.get_fare_rules(
                        benerail_client=self._benerail_client,
                        offer_obj=get_offer_res.offer_obj,
                    ),
                ),
                provider_company_id=self._provider_company_id,
            ),
            routing_key="offers.result.price",
        )


class OrdersConsumer(object):
    def __init__(
        self,
        consumer_obj: consumer.Consumer[orders_amqp_pb2.PlaceOrderTask],
        booking_offers_cache: cache.BookingOffersCache,
        producer_obj: producer.Producer,
        bookings: booking.BookingCreationHandler,
        provider_id: str,
    ):
        self._cache = booking_offers_cache
        self._consumer = consumer_obj
        self._producer = producer_obj
        self._bookings = bookings
        self._logger = stdout.get_logger()
        self._provider_id = provider_id

    async def consume(self) -> None:
        await self._consumer.consume(self._process_message)

    async def _process_message(
        self,
        message: types.Message[orders_amqp_pb2.PlaceOrderTask],
    ) -> None:
        booking_offer_details = await self._cache.fetch(
            message.body.booking.trip_option.price_quote_id,
        )
        message.body.booking.provider_name = _PROVIDER_NAME
        message.body.booking.provider_id = self._provider_id

        if not booking_offer_details:
            self._logger.warning(
                "No offer details found for booking",
                booking_id=message.body.booking.id,
                key=message.body.booking.trip_option.id,
            )

            return

        await self._producer.publish(
            await self._bookings.create_booking(message.body, booking_offer_details),
            routing_key="orders.result.offer",
        )


class SimpleSearchConsumer(object):
    def __init__(
        self,
        consumer_obj: consumer.Consumer[offers_amqp_pb2.SimpleTripOfferSearchTask],
        producer_obj: producer.Producer,
        benerail_offers_adapter: adapter.BenerailOffersAdapter,
        h3_mapping: h3.H3MappingRepository[train_stations.TrainStation],
        provider_company_id: str,
    ):
        self._consumer = consumer_obj
        self._producer = producer_obj
        self._adapter = benerail_offers_adapter
        self._station_mapping = h3_mapping
        self._provider_company_id = provider_company_id

    async def consume(self) -> None:
        await self._consumer.consume(self._process_message)

    async def _process_message(
        self,
        message: types.Message[offers_amqp_pb2.SimpleTripOfferSearchTask],
    ) -> None:
        trip_offer_groups = self._gather_simple_search_results(message.body)
        async for offer_group in trip_offer_groups:
            await self._producer.publish(
                msg=offers_amqp_pb2.TripOfferSearchResult(
                    offer_search_id=offer_group.id,
                    offer=offer_group,
                    provider_company_id=self._provider_company_id,
                ),
                routing_key="offers.result.trip",
            )

    async def _gather_simple_search_results(
        self,
        trip_offer_search: offers_amqp_pb2.SimpleTripOfferSearchTask,
    ) -> AsyncIterator[offers_pb2.OfferGroup]:
        allowed_segment_types = trip_offer_search.search.allowed_segment_types
        if models_pb2.Schedule.TYPE_RAIL in allowed_segment_types:
            search_origin = trip_offer_search.search.origin
            search_destination = trip_offer_search.search.destination
            origins = self._station_mapping.find_mapped_values(
                coordinates=search_origin.coordinates,
                neighbour_search_radius=1,
            )

            destinations = self._station_mapping.find_mapped_values(
                coordinates=search_destination.coordinates,
                neighbour_search_radius=1,
            )
            search_criteria = criteria.SearchCriteria(
                origin=_find_nearest_provider_place(
                    frozenset(origins),
                    search_origin.coordinates,
                ),
                destination=_find_nearest_provider_place(
                    frozenset(destinations),
                    search_destination.coordinates,
                ),
                passenger_dobs=[
                    protobuf.protobuf_to_date(passenger.date_of_birth)
                    for passenger in trip_offer_search.search.passengers
                ],
                outbound_departure_datetime=protobuf.protobuf_to_datetime(
                    trip_offer_search.search.departure_at,
                ),
                session_token=trip_offer_search.session_token,
            )
            offer_groups = self._adapter.gather_search_results(search_criteria)
            async for offer in offer_groups:
                yield offer


def _calculate_distance(
    p1: tuple[float, float],
    p2: train_stations.TrainStation,
) -> float:
    """Return the great circle distance in meters between two points."""
    station = p2.latitude, p2.longitude
    lon1, lat1, lon2, lat2 = map(math.radians, (*p1, *station))

    dlon = math.sin((lon2 - lon1) / 2) ** 2
    dlat = math.sin((lat2 - lat1) / 2) ** 2
    hav = dlat + math.cos(lat1) * math.cos(lat2) * dlon
    distance = 2 * math.asin(math.sqrt(hav))
    radius_of_earth_in_metres = 6371000
    return distance * radius_of_earth_in_metres


def _find_nearest_provider_place(
    stations: frozenset[train_stations.TrainStation],
    coordinates: latlng_pb2.LatLng,
) -> str:
    coords = coordinates.latitude, coordinates.longitude
    return min(
        stations,
        key=functools.partial(_calculate_distance, coords),
    ).identifier
