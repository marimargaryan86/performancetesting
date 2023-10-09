import ipaddress
import random
from collections.abc import Sequence

import pydantic
from motor import motor_asyncio

from snowfall.project.junction.plus.service.notifications.grpc import (
    ConfigurationVectorService,
    MonitoringRuleService,
    NotificationEventPublisherService,
    OrderService,
    SubscriberService,
)
from snowfall.project.junction.plus.service.notifications.notifications import (
    ConfigurationVectorRepository,
    MonitoringRuleRepository,
    OrderRepository,
    SubscriberRepository,
)
from snowfall.stdlib.service import amqp_factory, application
from snowfall.stdlib.transport.amqp import producer, types
from snowfall.stdlib.transport.grpc import server


class _GrpcSettings(application.Settings):
    grpc_address: ipaddress.IPv4Address = ipaddress.IPv4Address("127.0.0.1")
    grpc_port: int = 50051
    mongo_dsn: Sequence[pydantic.AnyUrl]
    amqp_dsn: pydantic.AmqpDsn


async def _serve(app: application.Application[_GrpcSettings]) -> None:
    mongo = motor_asyncio.AsyncIOMotorClient(
        str(random.choice(app.settings.mongo_dsn)),  # noqa: S311
    )
    connection = await amqp_factory.make_connection(app, app.settings.amqp_dsn)
    grpc_server = server.create_server(
        app.settings.grpc_address,
        app.settings.grpc_port,
        [
            OrderService(
                orders=OrderRepository(mongo.plus.orders),
                subscribers=SubscriberRepository(mongo.plus.subscribers),
            ),
            ConfigurationVectorService(
                configuration_vectors=ConfigurationVectorRepository(
                    mongo.plus.configuration_vectors,
                ),
            ),
            SubscriberService(
                subscribers=SubscriberRepository(mongo.plus.subscribers),
            ),
            MonitoringRuleService(
                monitoring_rules=MonitoringRuleRepository(
                    mongo.plus.monitoring_rules,
                ),
            ),
            NotificationEventPublisherService(
                producer_obj=producer.Producer(
                    connection=connection,
                    exchange=types.Exchange(name="plus_events"),
                ),
            ),
        ],
    )

    async with grpc_server.serve() as running:
        await running.wait_for_termination()


if __name__ == "__main__":
    entrypoint = application.Entrypoint(name="notifications")

    entrypoint.enter_with_commands(
        application.Command(
            name="grpc",
            callback=_serve,
            settings_class=_GrpcSettings,
        ),
    )
