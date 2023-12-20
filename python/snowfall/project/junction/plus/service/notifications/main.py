import ipaddress
import random
from collections.abc import Sequence

import httpx
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
from snowfall.vendor.consul.client import ConsulClient


class _GrpcSettings(application.Settings):
    grpc_address: ipaddress.IPv4Address = ipaddress.IPv4Address("127.0.0.1")
    grpc_port: int = 50051
    mongo_dsn: Sequence[pydantic.AnyUrl]
    cv_permissions: dict[str, list[str]] = pydantic.Field(default_factory=dict)
    consul_api_base_url: pydantic.AnyUrl
    consul_api_token: str
    consul_api_version: str = "v1"
    amqp_dsn: pydantic.AmqpDsn


async def _serve(app: application.Application[_GrpcSettings]) -> None:
    mongo = motor_asyncio.AsyncIOMotorClient(
        str(random.choice(app.settings.mongo_dsn)),  # noqa: S311
    )
    connection = await amqp_factory.make_connection(app, app.settings.amqp_dsn)
    http_client = await app.stack.enter_async_context(httpx.AsyncClient())
    consul_client = ConsulClient(
        api_base_url=str(app.settings.consul_api_base_url),
        api_token=app.settings.consul_api_token,
        version=app.settings.consul_api_version,
        httpx_client=http_client,
    )
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
                consul_client=consul_client,
                environment=app.environment,
                cv_permissions=app.settings.cv_permissions,
                subscribers=SubscriberRepository(mongo.plus.subscribers),
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
