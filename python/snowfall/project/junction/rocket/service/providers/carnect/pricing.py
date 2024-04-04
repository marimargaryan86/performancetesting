import datetime

from snowfall.project.junction.go.v1 import models_pb2 as common_pb2
from snowfall.project.junction.rocket.service.providers.carnect import cache, criteria
from snowfall.project.junction.rocket.service.providers.carnect.searches import (
    CarnectVehAvail,
    build_request,
    get_car_rental_result_detail,
    get_fare_rules,
    get_optional_value,
    parse_offer,
)
from snowfall.project.junction.rocket.service.searches.v1alpha import (
    amqp_pb2,
    models_pb2,
)
from snowfall.stdlib.format import protobuf
from snowfall.stdlib.logging import stdout
from snowfall.stdlib.transport.amqp import consumer, producer, types
from snowfall.stdlib.v1 import latlng_pb2
from snowfall.vendor.carnect import client, config
from snowfall.vendor.carnect.adapters import veh_avail_rate_adapter


class QuoteResultProducer:
    def __init__(self, producer_obj: producer.Producer, routing_key: str):
        self._producer = producer_obj
        self._routing_key = routing_key

    async def publish(self, message: amqp_pb2.QuoteTaskResult) -> None:
        await self._producer.publish(message, self._routing_key)


class QuoteTaskConsumer:
    def __init__(
        self,
        consumer_obj: consumer.Consumer[amqp_pb2.QuoteTask],
        quote_result_producer: QuoteResultProducer,
        search_result_cache: cache.SearchResultCache,
        quote_cache: cache.QuoteCache,
        carnect_client: client.CarnectClient,
        carnect_config: config.Config,
        ttl: datetime.timedelta,
    ):
        self._consumer = consumer_obj
        self._quote_result_producer = quote_result_producer
        self._search_result_cache = search_result_cache
        self._quote_cache = quote_cache
        self._client = carnect_client
        self._config = carnect_config
        self._ttl = ttl
        self._logger = stdout.get_logger()

    async def consume(self) -> None:
        await self._consumer.consume(self._process_message)

    async def _process_message(
        self,
        message: types.Message[amqp_pb2.QuoteTask],
    ) -> None:
        offer_cache = await self._search_result_cache.fetch(message.body.quote.offer_id)

        if not offer_cache:
            return

        veh_avail = await self._get_matching_quote(offer_cache)

        if veh_avail is None:
            self._logger.error(
                "Failed to match cached offer",
                offer_cache=offer_cache.dict(),
            )
            return

        try:
            quote_id = veh_avail.veh_avail_core.reference.id_context  # type: ignore[union-attr]
        except AttributeError:
            self._logger.exception(
                "Failed to get quote id",
                offer_cache=offer_cache.dict(),
            )
            return

        if quote_id is None:
            self._logger.error(
                "Failed to get quote id",
                offer_cache=offer_cache.dict(),
            )
            return

        offer = parse_offer(veh_avail)
        expires_at = datetime.datetime.now(tz=datetime.UTC) + self._ttl

        price_quote = cache.PriceQuote(
            quote_id=quote_id,
        )
        price_quote_id = await self._quote_cache.store(
            record=price_quote,
            expires_at=expires_at,
        )
        quote_obj = models_pb2.Quote(
            id=price_quote_id,
            expires_at=protobuf.datetime_to_protobuf(expires_at),
            price=offer.price,
            price_breakdown=offer.price_breakdown,
            conditional_prices=offer.car_rental.conditional_prices,
            rules=get_fare_rules(veh_avail),
        )

        quote_obj.MergeFrom(message.body.quote)

        await self._quote_result_producer.publish(
            amqp_pb2.QuoteTaskResult(
                quote=quote_obj,
                reseller_id=message.body.reseller_id,
            ),
        )

    async def _get_matching_quote(
        self,
        offer_details: cache.CarRentalResultDetail,
    ) -> CarnectVehAvail | None:
        search_task = criteria.Criteria(
            search_id="",
            origin=common_pb2.Point(
                coordinates=latlng_pb2.LatLng(
                    latitude=offer_details.origin.latitude,
                    longitude=offer_details.origin.longitude,
                ),
            ),
            destination=common_pb2.Point(
                coordinates=latlng_pb2.LatLng(
                    latitude=offer_details.destination.latitude,
                    longitude=offer_details.destination.longitude,
                ),
            ),
            pickup_datetime=offer_details.departure_at,
            return_datetime=offer_details.arrival_at,
            driver_age=offer_details.driver_age,
        )
        response = await self._client.get_avail_rate(
            build_request(
                search_task=search_task,
                carnect_config=self._config,
                vendor_code=offer_details.vendor_code,
            ),
        )

        rs_adapter = veh_avail_rate_adapter.VehAvailRateAdapter(response)

        if not rs_adapter.is_success():
            self._logger.error(
                "VehAvailRate search failed",
                criteria=str(search_task),
                message=rs_adapter.get_error(),
            )
            return None

        for availability_type in rs_adapter.available():
            veh_avails = get_optional_value(
                availability_type,
                "veh_avails.veh_avail",
                [],
            )

            for veh_avail in veh_avails:
                details = get_car_rental_result_detail(veh_avail)
                if self._match_details(details, offer_details):
                    return veh_avail
        return None

    def _match_details(
        self,
        details: models_pb2.CarRentalResultDetail,
        offer_details: cache.CarRentalResultDetail,
    ) -> bool:
        return all((
            details.origin.coordinates.latitude == offer_details.origin.latitude,
            details.origin.coordinates.longitude == offer_details.origin.longitude,
            details.destination.coordinates.latitude
            == offer_details.destination.latitude,
            details.destination.coordinates.longitude
            == offer_details.destination.longitude,
            details.model == offer_details.model,
            details.seats_count == offer_details.seats_count,
            details.doors_count == offer_details.doors_count,
            details.transmission == offer_details.transmission,
            details.baggage_quantity == offer_details.baggage_quantity,
            details.vehicle_type == offer_details.vehicle_type,
            details.vendor_name == offer_details.vendor_name,
            details.vendor_code == offer_details.vendor_code,
        ))
