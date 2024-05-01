import contextlib

import httpx

from snowfall.project.junction.rocket.provider import service as provider_service
from snowfall.project.junction.rocket.service.providers.benerail import (
    adapter,
    cache,
    config,
    helper_functions,
)
from snowfall.project.junction.rocket.service.providers.benerail import (
    pricing as provider_pricing,
)
from snowfall.stdlib.service import amqp_factory, redis_factory
from snowfall.stdlib.transport.amqp import consumer, producer, types
from snowfall.vendor.benerail import client


async def pricing(app: provider_service.Application[config.PricingSettings]) -> None:
    async with contextlib.AsyncExitStack() as stack:
        http_client = await stack.enter_async_context(
            httpx.AsyncClient(
                http2=True,
                cert=helper_functions.cert_tmp_path(app.settings.cert_base64),
            ),
        )
        benerail_client = client.BenerailClient(
            subscription_key=app.settings.subscription_key,
            base_url=str(app.settings.api_base_url),
            http_client=http_client,
        )
        connection = await amqp_factory.make_connection(app, app.settings.amqp_dsn)
        redis_client = await redis_factory.make_client(
            app=app,
            dsn=app.settings.redis_dsn,
            decode_responses=False,
        )
        quote_task_consumer = provider_pricing.QuoteTaskConsumer(
            consumer_obj=consumer.Consumer(
                connection=connection,
                queue_name="{0}_pricing_consumer".format(app.name),
                binds=[(types.Exchange("searches"), "searches.pricing")],
            ),
            quote_result_producer=provider_pricing.QuoteResultProducer(
                producer_obj=producer.Producer(connection, types.Exchange("searches")),
                routing_key="searches.pricing_results",
            ),
            search_result_cache=cache.OffersCache(client=redis_client),
            quote_cache=cache.BookingOffersCache(client=redis_client),
            benerail_adapter=adapter.BenerailAdapter(benerail_client),
            client=benerail_client,
            ttl=app.settings.ttl,
            pay_company_id=app.settings.pay_company_id,
        )
        await quote_task_consumer.consume()
