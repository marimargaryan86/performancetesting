import contextlib

import httpx
from redis import asyncio as aioredis

from snowfall.project.junction.service.providers.benerail import cache, config, consumer
from snowfall.stdlib.instrumentation.httpx import logging, metrics
from snowfall.stdlib.persistence.redis import types as redis_types
from snowfall.stdlib.service import amqp_factory, application
from snowfall.stdlib.transport.amqp import consumer as std_consumer
from snowfall.stdlib.transport.amqp import producer, types
from snowfall.vendor.benerail import client


async def price_quotes(app: application.Application[config.PriceQuoteSettings]) -> None:
    async with contextlib.AsyncExitStack() as stack:
        redis_connection: aioredis.Redis[bytes] = await stack.enter_async_context(
            aioredis.from_url(
                str(app.settings.redis_dsn),
                decode_responses=False,
                retry_on_error=[aioredis.ConnectionError],
            ).client(),
        )
        offer_cache = cache.OffersCache(
            client=redis_types.Client[bytes](redis_connection, prefix=app.name),
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
            offer_cache=offer_cache,
            benerail_client=client.BenerailClient(
                subscription_key=app.settings.subscription_key,
                base_url=str(app.settings.api_base_url),
                http_client=http_client,
            ),
            price_ttl=app.settings.ttl,
            provider_company_id=app.settings.provider_company_id,
        ).consume()
