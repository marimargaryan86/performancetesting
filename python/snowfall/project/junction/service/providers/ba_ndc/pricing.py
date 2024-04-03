import datetime

from snowfall.project.junction.go.service.offers.v1 import amqp_pb2 as offers_amqp_pb2
from snowfall.project.junction.provider import airports
from snowfall.project.junction.service.providers.ba_ndc import (
    ba_ndc_helpers,
    cache,
    config,
    pricing_transformer,
)
from snowfall.stdlib.persistence import filesystem
from snowfall.stdlib.service import (
    amqp_factory,
    application,
    grpc_factory,
    httpx_factory,
    redis_factory,
)
from snowfall.stdlib.transport.amqp import consumer as amqp_consumer
from snowfall.stdlib.transport.amqp import producer
from snowfall.stdlib.transport.amqp import types as amqp_types
from snowfall.vendor.ba_ndc import client
from snowfall.vendor.rate_limiter import client as rate_limiter_client
from snowfall.vendor.rate_limiter import gubernator_pb2_grpc


async def price_quotes(
    app: application.Application[config.PricingSettings],
) -> None:
    redis_client = await redis_factory.make_client(
        app=app,
        dsn=app.settings.redis_dsn,
        decode_responses=False,
    )
    amqp_connection = await amqp_factory.make_connection(app, app.settings.amqp_dsn)
    offer_cache = cache.OfferCache(
        client=redis_client,
    )

    await PriceQuoteConsumer(
        consumer_obj=amqp_consumer.Consumer(
            connection=amqp_connection,
            queue_name="{0}_prices".format(app.name),
            binds=[(amqp_types.Exchange("prices"), "offers.pricing")],
        ),
        producer_obj=producer.Producer(
            connection=amqp_connection,
            exchange=amqp_types.Exchange("prices"),
        ),
        offer_cache=offer_cache,
        price_quote_cache=cache.PriceQuoteCache(client=redis_client),
        provider_company_id=app.settings.provider_company_id,
        price_ttl=app.settings.ttl,
        ba_ndc_client=await _ba_ndc_client_factory(app),
        airport_repository=airports.AirportRepository(
            airports_data=filesystem.PkgLoader("snowfall.data").load("airports.json"),
        ),
    ).consume()


async def _ba_ndc_client_factory(
    app: application.Application[config.PricingSettings],
) -> client.BaNdcClient:
    http_client = await httpx_factory.make_client(app)
    rate_limit_client = rate_limiter_client.Client(
        gubernator_pb2_grpc.V1Stub(
            await grpc_factory.make_insecure_channel(
                app,
                app.settings.rate_limiter_grpc_host,
            ),
        ),
        app.settings.rate_limiter_service_configs["ba-ndc"],
    )
    rate_limit_client_daily = rate_limiter_client.Client(
        gubernator_pb2_grpc.V1Stub(
            await grpc_factory.make_insecure_channel(
                app,
                app.settings.rate_limiter_grpc_host,
            ),
        ),
        app.settings.rate_limiter_service_configs["ba-ndc-daily"],
    )

    return client.BaNdcClient(
        api_base_url=str(app.settings.api_base_url),
        api_key=app.settings.api_key,
        http_client=http_client,
        rate_limit_clients=(rate_limit_client, rate_limit_client_daily),
    )


class PriceQuoteConsumer:
    def __init__(
        self,
        consumer_obj: amqp_consumer.Consumer[offers_amqp_pb2.TripPriceQuoteTask],
        producer_obj: producer.Producer,
        offer_cache: cache.OfferCache,
        price_quote_cache: cache.PriceQuoteCache,
        provider_company_id: str,
        price_ttl: datetime.timedelta,
        ba_ndc_client: client.BaNdcClient,
        airport_repository: airports.AirportRepository,
    ):
        self._offer_cache = offer_cache
        self._price_quote_cache = price_quote_cache
        self._consumer = consumer_obj
        self._logger = ba_ndc_helpers.get_logger(__name__)
        self._producer = producer_obj
        self._transformer = pricing_transformer.PriceQuoteTransformer()
        self._ttl = price_ttl
        self._provider_company_id = provider_company_id
        self._ba_ndc_client = ba_ndc_client
        self._airport_repository = airport_repository

    async def consume(self) -> None:
        await self._consumer.consume(self._process_message)

    async def _process_message(
        self,
        amqp_message: amqp_types.Message[offers_amqp_pb2.TripPriceQuoteTask],
    ) -> None:
        offer_details = await self._offer_cache.fetch(amqp_message.body.option_id)

        if not offer_details:
            return

        refreshed_offer = await self._ba_ndc_client.get_offer(
            offer_id=offer_details.offer_id,
        )

        price_quote_details = cache.PriceQuoteDetails(
            offer_id=refreshed_offer.offer.identifier,
            passengers=[
                cache.OfferDetailsPassenger(
                    identifier=passenger_info.identifier,
                    passenger_type=passenger_info.passenger_type.name,
                )
                for passenger_info in refreshed_offer.passengers
            ],
            price=cache.Price(
                amount=refreshed_offer.offer.price.total_amount,
                currency=refreshed_offer.offer.price.currency,
            ),
            price_breakdown=cache.PriceBreakdown(
                currency=refreshed_offer.offer.price.currency,
                base_amount=refreshed_offer.offer.price.base_amount,
                tax_amount=refreshed_offer.offer.price.tax_amount,
            ),
            is_international_flight=offer_details.is_international_flight,
            has_flight_with_usa_destination=offer_details.has_flight_with_usa_destination,
            expires_at=refreshed_offer.expires_at,
            penalties=[
                cache.OfferPenalty(
                    penalty_type=penalty.penalty_type.name,
                    price=cache.Price(
                        currency=penalty.price.currency,
                        amount=penalty.price.total_amount,
                    ),
                )
                for penalty in refreshed_offer.penalties
                if penalty.price
            ],
        )

        expires_at = datetime.datetime.now(tz=datetime.UTC) + self._ttl

        price_quote_details_id = await self._price_quote_cache.store(
            price_quote_details,
            expires_at,
        )

        await self._producer.publish(
            offers_amqp_pb2.TripPriceQuoteResult(
                price_quote_container_id=amqp_message.body.price_quote_container_id,
                option_id=amqp_message.body.option_id,
                price_quote=self._transformer.to_price_quote(
                    price_quote_details_id=price_quote_details_id,
                    price_quote_details=price_quote_details,
                    option_id=amqp_message.body.option_id,
                ),
                provider_company_id=self._provider_company_id,
            ),
            routing_key="offers.result.price",
        )
