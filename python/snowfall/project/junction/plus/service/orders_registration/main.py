import httpx
import pydantic

from snowfall.project.junction.plus.adapter import orders
from snowfall.project.junction.plus.service.notifications.v1alpha import (
    grpc_pb2_grpc as notifications_pb2_grpc,
)
from snowfall.project.junction.plus.service.orders_registration import importer
from snowfall.stdlib import service
from snowfall.stdlib.instrumentation.httpx import logging, metrics
from snowfall.stdlib.transport.amqp import consumer, producer, types
from snowfall.stdlib.transport.grpc.client import create_channel


class _ImportSettings(service.Settings):
    amqp_dsn: pydantic.AnyUrl
    notifications_address: str


async def _import(app: service.AsyncApplication[_ImportSettings]) -> None:
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
        producer_obj=producer.Producer(
            connection=connection,
            exchange=types.Exchange(name="plus_events"),
        ),
        orders=orders.GrpcClient(
            orders=notifications_pb2_grpc.OrderServiceStub(
                create_channel(app.settings.notifications_address),
            ),
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
