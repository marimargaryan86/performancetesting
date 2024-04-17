from snowfall.project.junction.plus.adapter import (
    monitoring_rules,
    notification_event_publisher,
    orders,
    subscribers,
)
from snowfall.project.junction.plus.service.notifications.v1 import (
    grpc_pb2_grpc as notifications_pb2_grpc,
)
from snowfall.project.junction.plus.service.weather_report import open_weather_map
from snowfall.project.junction.plus.service.weather_report.cron import (
    WeatherReportCronJob,
)
from snowfall.stdlib.service import application, grpc_factory


class _CronSettings(application.Settings):
    notifications_address: str
    owm_key: str
    owm_url: str


async def _cron_run(
    app: application.Application[_CronSettings],
) -> None:
    notifications_channel = await grpc_factory.make_insecure_channel(
        app,
        app.settings.notifications_address,
    )

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
        orders=orders.GrpcClient(
            orders=notifications_pb2_grpc.OrderServiceStub(
                notifications_channel,
            ),
        ),
        publisher_client=notification_event_publisher.GrpcClient(
            notification_event_publisher=notifications_pb2_grpc.NotificationEventPublisherServiceStub(
                notifications_channel,
            ),
        ),
        open_weather_map_client=open_weather_map.OpenWeatherMapClient(
            api_url=app.settings.owm_url,
            api_key=app.settings.owm_key,
        ),
    )

    await job.run()


if __name__ == "__main__":
    entrypoint = application.Entrypoint(name="junction-plus-weather-report")

    entrypoint.enter_with_commands(
        application.Command(
            name="cron",
            callback=_cron_run,
            settings_class=_CronSettings,
        ),
    )
