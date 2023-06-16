import random
from collections.abc import Sequence

import httpx
import pydantic
from motor import motor_asyncio

from snowfall.project.junction.plus.service.orders_registration import (
    importer,
    orders_registration,
)
from snowfall.stdlib import service
from snowfall.stdlib.instrumentation.httpx import logging, metrics
from snowfall.stdlib.transport.amqp import consumer, types


class _ImportSettings(service.Settings):
    amqp_dsn: pydantic.AnyUrl
    mongo_dsn: Sequence[pydantic.AnyUrl]


async def _import(app: service.AsyncApplication[_ImportSettings]) -> None:
    mongo = motor_asyncio.AsyncIOMotorClient(
        random.choice(app.settings.mongo_dsn),  # nosec
    )

    http_client = await app.stack.enter_async_context(httpx.AsyncClient())
    connection = await app.stack.enter_async_context(
        types.Connection(
            app.settings.amqp_dsn,
        ),
    )

    logging.register(http_client)
    metrics.register(http_client)

    order_importer = importer.OrderImporter(
        consumer_obj=consumer.Consumer(
            connection=connection,
            queue_name="plus_{0}".format(app.name),
            binds=[(types.Exchange("plus_import_orders"), "plus.orders")],
        ),
        order_repository=orders_registration.OrderRepository(
            mongo.plus.orders,
        ),
    )
    await order_importer.consume()


if __name__ == "__main__":
    entrypoint = service.Entrypoint(name="orders_registration")

    entrypoint.enter_with_commands(
        service.Command(
            name="import",
            callback=_import,
            settings_class=_ImportSettings,
        ),
    )
