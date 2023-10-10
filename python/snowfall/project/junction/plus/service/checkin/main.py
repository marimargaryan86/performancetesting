import ipaddress

from snowfall.project.junction.plus.adapter import (
    monitoring_rules,
    notification_event_publisher,
    subscribers,
)
from snowfall.project.junction.plus.service.checkin.cron import CheckinCronJob
from snowfall.project.junction.plus.service.checkin.grpc import CheckinService
from snowfall.project.junction.plus.service.notifications.v1alpha import (
    grpc_pb2_grpc as notifications_pb2_grpc,
)
from snowfall.stdlib.service import application, grpc_factory
from snowfall.stdlib.transport.grpc import server


class _GrpcSettings(application.Settings):
    grpc_address: ipaddress.IPv4Address = ipaddress.IPv4Address("127.0.0.1")
    grpc_port: int = 50051


class _CronSettings(application.Settings):
    notifications_address: str


async def _serve(app: application.Application[_GrpcSettings]) -> None:
    grpc_server = server.create_server(
        app.settings.grpc_address,
        app.settings.grpc_port,
        [
            CheckinService(),
        ],
    )

    async with grpc_server.serve() as running:
        await running.wait_for_termination()


async def _cron_run(
    app: application.Application[_CronSettings],
) -> None:
    notifications_channel = await grpc_factory.make_insecure_channel(
        app,
        app.settings.notifications_address,
    )

    job = CheckinCronJob(
        monitoring_rules=monitoring_rules.GrpcClient(
            monitoring_rules=notifications_pb2_grpc.MonitoringRuleServiceStub(
                notifications_channel,
            ),
        ),
        subscribers=subscribers.GrpcClient(
            subscribers=notifications_pb2_grpc.SubscriberServiceStub(
                notifications_channel,
            ),
        ),
        publisher_client=notification_event_publisher.GrpcClient(
            notification_event_publisher=notifications_pb2_grpc.NotificationEventPublisherServiceStub(
                notifications_channel,
            ),
        ),
    )

    await job.run()


if __name__ == "__main__":
    entrypoint = application.Entrypoint(name="checkin")

    entrypoint.enter_with_commands(
        application.Command(
            name="grpc",
            callback=_serve,
            settings_class=_GrpcSettings,
        ),
        application.Command(
            name="cron",
            callback=_cron_run,
            settings_class=_CronSettings,
        ),
    )
