import httpx
import pydantic

from snowfall.project.junction.plus.adapter import (
    monitoring_rules,
    orders,
)
from snowfall.project.junction.plus.service.notifications.v1alpha import (
    grpc_pb2_grpc as notifications_pb2_grpc,
)
from snowfall.project.junction.plus.service.orders_registration import (
    flight_stats,
    importer,
)
from snowfall.stdlib.instrumentation.httpx import logging, metrics
from snowfall.stdlib.service import amqp_factory, application, grpc_factory
from snowfall.stdlib.transport.amqp import consumer, producer, types


class _ImportSettings(application.Settings):
    amqp_dsn: pydantic.AmqpDsn
    notifications_address: str
    flight_stats_api_url: str
    flight_stats_app_id: str
    flight_stats_app_key: str
    flight_stats_webhook_url: str


async def _import(app: application.Application[_ImportSettings]) -> None:
    http_client = await app.stack.enter_async_context(httpx.AsyncClient())
    connection = await amqp_factory.make_connection(app, app.settings.amqp_dsn)

    logging.register(http_client)
    metrics.register(http_client)
    notifications_channel = await grpc_factory.make_insecure_channel(
        app,
        app.settings.notifications_address,
    )
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
            orders=notifications_pb2_grpc.OrderServiceStub(notifications_channel),
        ),
        monitoring_rules=monitoring_rules.GrpcClient(
            monitoring_rules=notifications_pb2_grpc.MonitoringRuleServiceStub(
                notifications_channel,
            ),
        ),
        flight_stats_client=flight_stats.FlightStatsClient(
            app.settings.flight_stats_api_url,
            app.settings.flight_stats_app_id,
            app.settings.flight_stats_app_key,
            app.settings.flight_stats_webhook_url,
        ),
    )
    await order_importer.consume()


if __name__ == "__main__":
    entrypoint = application.Entrypoint(name="orders-registration")

    entrypoint.enter_with_commands(
        application.Command(
            name="import",
            callback=_import,
            settings_class=_ImportSettings,
        ),
    )
