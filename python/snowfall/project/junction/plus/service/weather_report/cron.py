from snowfall.project.junction.plus.adapter import (
    monitoring_rules as monitoring_rules_adapter,
)
from snowfall.project.junction.plus.adapter import (
    notification_event_publisher as notification_event_publisher_adapter,
)
from snowfall.project.junction.plus.adapter import subscribers as subscribers_adapter
from snowfall.stdlib.logging import stdout

_CC_MAX_PAIR_SIZE = 2450


class WeatherReportCronJob(object):
    def __init__(
        self,
        monitoring_rules: monitoring_rules_adapter.Client,
        subscribers: subscribers_adapter.Client,
        publisher_client: notification_event_publisher_adapter.Client,
    ) -> None:
        self._monitoring_rules = monitoring_rules
        self._subscribers = subscribers
        self._publisher_client = publisher_client
        self._logger = stdout.get_logger()

    async def run(self) -> None:
        self._logger.info("Started weather reporter as a cron job")
