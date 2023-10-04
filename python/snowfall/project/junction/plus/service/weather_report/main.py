from snowfall.project.junction.plus.adapter import (
    monitoring_rules,
    notification_event_publisher,
    subscribers,
)
from snowfall.project.junction.plus.service.notifications.v1alpha import (
    grpc_pb2_grpc as notifications_pb2_grpc,
)
from snowfall.project.junction.plus.service.weather_report.cron import (
    WeatherReportCronJob,
)
from snowfall.stdlib.service import application
from snowfall.stdlib.transport.grpc.client import create_channel


class _CronSettings(application.Settings):
    notifications_address: str


async def _cron_run(
    app: application.AsyncApplication[_CronSettings],
) -> None:
    notifications_channel = create_channel(app.settings.notifications_address)

    job = WeatherReportCronJob(
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
    entrypoint = application.Entrypoint(name="weather-report")

    entrypoint.enter_with_commands(
        application.Command(
            name="cron",
            callback=_cron_run,
            settings_class=_CronSettings,
        ),
    )
