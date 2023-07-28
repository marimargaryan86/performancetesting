import datetime

import httpx
from redis import asyncio as aioredis

from snowfall.project.junction.go.service.offers.v1 import amqp_pb2 as offers_amqp_pb2
from snowfall.project.junction.go.service.offers.v1 import models_pb2 as offers_pb2
from snowfall.project.junction.service.providers.distribusion import cache, config
from snowfall.stdlib import money, service
from snowfall.stdlib.format import protobuf
from snowfall.stdlib.instrumentation.httpx import logging, metrics
from snowfall.stdlib.logging import stdout
from snowfall.stdlib.persistence.redis import types as redis
from snowfall.stdlib.transport.amqp import consumer, producer, types
from snowfall.vendor.distribusion import client
from snowfall.vendor.distribusion.models import connections, criterias
from snowfall.vendor.rate_limiter.client import Client as RateLimitClient


class NoPricingError(Exception):
    """Raised when a failed pricing result is received."""


async def price_quotes(  # noqa: WPS210
    app: service.AsyncApplication[config.PricingSettings],
) -> None:
    http_client = await app.stack.enter_async_context(
        httpx.AsyncClient(
            timeout=app.settings.api_timeout,
        ),
    )
    logging.register(http_client)
    metrics.register(http_client)
    rate_limit_client = await app.stack.enter_async_context(
        RateLimitClient(
            app.settings.rate_limiter_grpc_host,
            app.settings.rate_limiter_service_configs["distribusion"],
        ),
    )
    redis_connection: aioredis.Redis[bytes] = await app.stack.enter_async_context(
        aioredis.from_url(
            app.settings.redis_dsn[0],
            decode_responses=False,
        ).client(),
    )
    distribusion_client = client.DistribusionClient(
        api_base_url=app.settings.api_base_url,
        api_key=app.settings.api_key,
        retailer_partner_number=app.settings.retailer_partner_number,
        http_client=http_client,
        rate_limit_client=rate_limit_client,
    )
    amqp_connection = await app.stack.enter_async_context(
        types.Connection(app.settings.amqp_dsn),
    )
    offer_cache = cache.OffersCache(
        client=redis.Client[bytes](redis_connection, prefix=app.name),
    )
    await PriceQuoteConsumer(
        distribusion_client=distribusion_client,
        consumer_obj=consumer.Consumer(
            connection=amqp_connection,
            queue_name="{0}_prices".format(app.name),
            binds=[(types.Exchange("prices"), "offers.pricing")],
        ),
        producer_obj=producer.Producer(
            connection=amqp_connection,
            exchange=types.Exchange("prices"),
        ),
        offer_cache=offer_cache,
        provider_company_id=app.settings.provider_company_id,
        ttl=app.settings.ttl,
    ).consume()


class PriceQuoteConsumer(object):
    def __init__(  # noqa: WPS211
        self,
        distribusion_client: client.DistribusionClient,
        consumer_obj: consumer.Consumer[offers_amqp_pb2.TripPriceQuoteTask],
        producer_obj: producer.Producer,
        offer_cache: cache.OffersCache,
        provider_company_id: str,
        ttl: datetime.timedelta,
    ):
        self._client = distribusion_client
        self._cache = offer_cache
        self._consumer = consumer_obj
        self._logger = stdout.get_logger()
        self._producer = producer_obj
        self._provider_company_id = provider_company_id
        self._ttl = ttl

    async def consume(self) -> None:
        await self._consumer.consume(self._process_message)

    async def _process_message(
        self,
        amqp_message: types.Message[offers_amqp_pb2.TripPriceQuoteTask],
    ) -> None:
        offer_details = await self._cache.fetch(amqp_message.body.option_id)

        if not offer_details:
            return

        connection_vacancy = await self._vacancy(offer_details)

        if not connection_vacancy.vacant:
            raise NoPricingError("Pricing did not succeed.")

        offer_details.price = connection_vacancy.total_price or offer_details.price
        offer_details.currency = connection_vacancy.currency
        expires_at = datetime.datetime.now(tz=datetime.UTC) + self._ttl
        price_quote_id = await self._cache.store(offer_details, expires_at)

        price_quote_price = money.Money(
            amount=offer_details.price,
            currency=money.Currency(offer_details.currency),
        ).protobuf()

        await self._producer.publish(
            offers_amqp_pb2.TripPriceQuoteResult(
                price_quote_container_id=amqp_message.body.price_quote_container_id,
                option_id=amqp_message.body.option_id,
                price_quote=offers_pb2.PriceQuote(
                    id=price_quote_id,
                    option_id=amqp_message.body.option_id,
                    expires_at=protobuf.datetime_to_protobuf(
                        offer_details.expires_at,
                    ),
                    price=price_quote_price,
                    price_breakdown=[
                        offers_pb2.PriceBreakdown(
                            price=price_quote_price,
                            breakdown_type=offers_pb2.PriceBreakdown.BreakdownType.BREAKDOWN_TYPE_BASE_FARE,
                        ),
                    ],
                    rules=[
                        offers_pb2.FareRule(
                            title=fare_rule.name,
                            body=fare_rule.description,
                        )
                        for fare_rule in offer_details.fare_rules or []
                    ],
                    penalties=self._create_penalties(offer_details),
                ),
                provider_company_id=self._provider_company_id,
            ),
            routing_key="offers.result.price",
        )

    def _create_penalties(
        self,
        offer_details: cache.OfferDetails,
    ) -> list[offers_pb2.Penalty]:
        res = []

        if offer_details.fully_refundable:
            res.append(
                offers_pb2.Penalty(
                    penalty_type=offers_pb2.Penalty.Type.TYPE_REFUND,
                    refundable=True,
                    applicability=offers_pb2.Penalty.Applicability.APPLICABILITY_BEFORE,
                ),
            )

        if offer_details.non_refundable:
            res.append(
                offers_pb2.Penalty(
                    penalty_type=offers_pb2.Penalty.Type.TYPE_REFUND,
                    refundable=False,
                    applicability=offers_pb2.Penalty.Applicability.APPLICABILITY_BEFORE,
                ),
            )

        if offer_details.changeable:
            res.append(
                offers_pb2.Penalty(
                    penalty_type=offers_pb2.Penalty.Type.TYPE_EXCHANGE,
                    changeable=True,
                    applicability=offers_pb2.Penalty.Applicability.APPLICABILITY_BEFORE,
                    conditions_apply=offer_details.has_exchange_conditions or False,
                ),
            )

        return res

    async def _vacancy(
        self,
        offer_details: cache.OfferDetails,
    ) -> connections.ConnectionVacancy:
        count_pax_type = self._count_passenger_type(offer_details)
        connection_vacancy_criteria = criterias.ConnectionVacancyCriteria(
            marketing_carrier=offer_details.marketing_carrier,
            departure_station=offer_details.departure_station,
            arrival_station=offer_details.arrival_station,
            departure_time=offer_details.departure_time,
            arrival_time=offer_details.arrival_time,
            fare_class=offer_details.fare_class,
            pax=[],
            passenger_type=[],
            currency=offer_details.currency,
        )

        for key, item_value in count_pax_type.items():
            connection_vacancy_criteria.passenger_type.append(key)
            connection_vacancy_criteria.pax.append(item_value)

        return await self._client.get_connection_vacancy(
            connection_vacancy_criteria,
        )

    def _count_passenger_type(
        self,
        offer_details: cache.OfferDetails,
    ) -> dict[str, int]:
        types_count = {}
        for age in offer_details.passengers_age:
            for pax_type in offer_details.passenger_types:
                if pax_type.min_age <= age <= pax_type.max_age:
                    type_code = pax_type.type_code

                    if type_code not in types_count:
                        types_count[type_code] = 1  # noqa: WPS220
                    else:
                        types_count[type_code] += 1

        return types_count
