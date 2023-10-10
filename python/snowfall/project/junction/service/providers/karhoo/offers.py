import httpx

from snowfall.project.junction.service.providers.karhoo import cache, config, consumer
from snowfall.stdlib.instrumentation.httpx import logging, metrics
from snowfall.stdlib.service import amqp_factory, application, redis_factory
from snowfall.stdlib.transport.amqp import consumer as amqp_consumer
from snowfall.stdlib.transport.amqp import producer as amqp_producer
from snowfall.stdlib.transport.amqp import trackable, types
from snowfall.vendor.karhoo import client


async def offers(
    app: application.Application[config.OfferSettings],
) -> None:
    http_client = await app.stack.enter_async_context(
        httpx.AsyncClient(
            timeout=app.settings.api_timeout.seconds,
        ),
    )
    logging.register(http_client)
    metrics.register(http_client)
    amqp_connection = await amqp_factory.make_connection(app, app.settings.amqp_dsn)

    redis_client = await redis_factory.make_client(
        app=app,
        dsn=app.settings.redis_dsn,
        decode_responses=False,
    )
    karhoo_client = client.KarhooClient(
        base_url=str(app.settings.api_base_url),
        api_key=app.settings.api_key,
        http_client=http_client,
    )

    trip_offer_search_consumer = consumer.TripOfferSearchConsumer(
        consumer_obj=amqp_consumer.Consumer(
            connection=amqp_connection,
            queue_name="{0}_searches".format(app.name),
            binds=[(types.Exchange("offers"), "offers.search.trip")],
            middleware_stack=[
                trackable.ReportingMiddleware(
                    status_reporter=trackable.StatusReporter(
                        producer=amqp_producer.Producer(
                            connection=amqp_connection,
                            exchange=types.Exchange("karhoo"),
                        ),
                    ),
                ).execute,
            ],
        ),
        producer_obj=amqp_producer.Producer(
            connection=amqp_connection,
            exchange=types.Exchange("offers"),
        ),
        karhoo_client=karhoo_client,
        redis=redis_client,
        ttl=app.settings.ttl,
        offers_cache=cache.OffersCache(
            client=redis_client,
        ),
        polling_wait_time_in_seconds=app.settings.polling_wait_time_seconds,
        polling_retries_attempts=app.settings.polling_retries_attempts,
        provider_company_id=app.settings.provider_company_id,
    )

    await trip_offer_search_consumer.consume()
