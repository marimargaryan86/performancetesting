import contextlib

import httpx

from snowfall.project.junction.service.providers.benerail import (
    adapter,
    cache,
    config,
    consumer,
)
from snowfall.stdlib.instrumentation.httpx import logging, metrics
from snowfall.stdlib.service import amqp_factory, application, redis_factory
from snowfall.stdlib.transport.amqp import consumer as std_consumer
from snowfall.stdlib.transport.amqp import producer, types
from snowfall.vendor.benerail import client


async def price_quotes(app: application.Application[config.PriceQuoteSettings]) -> None:
    async with contextlib.AsyncExitStack() as stack:
        redis_client = await redis_factory.make_client(
            app=app,
            dsn=app.settings.redis_dsn,
            decode_responses=False,
        )
        amqp_connection = await amqp_factory.make_connection(app, app.settings.amqp_dsn)
        http_client = await stack.enter_async_context(
            httpx.AsyncClient(
                http2=True,
                timeout=app.settings.api_timeout.seconds,
                cert=config.cert_tmp_path(app.settings.cert_base64),
            ),
        )
        logging.register(http_client)
        metrics.register(http_client)
        benerail_client = client.BenerailClient(
            subscription_key=app.settings.subscription_key,
            base_url=str(app.settings.api_base_url),
            http_client=http_client,
        )

        await consumer.PriceQuoteConsumer(
            consumer_obj=std_consumer.Consumer(
                connection=amqp_connection,
                queue_name="{0}_prices".format(app.name),
                binds=[(types.Exchange("prices"), "offers.pricing")],
            ),
            producer_obj=producer.Producer(
                connection=amqp_connection,
                exchange=types.Exchange("prices"),
            ),
            cache_container=cache.Cache(
                offers_cache=cache.OffersCache(
                    client=redis_client,
                ),
                booking_offers_cache=cache.BookingOffersCache(
                    client=redis_client,
                ),
            ),
            benerail_client=benerail_client,
            benerail_adapter=adapter.BenerailAdapter(benerail_client),
            price_ttl=app.settings.ttl,
            provider_company_id=app.settings.provider_company_id,
        ).consume()
