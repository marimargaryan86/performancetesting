from typing import Sequence

import lagom
from pydantic import AnyUrl

from snowfall.project.junction.plus.service.poc_api import (
    flight_stats_client,
    repository,
    twilio,
)
from snowfall.stdlib.integration.starlette import application
from snowfall.stdlib.persistence.redis import types as redis
from snowfall.vendor.junction.go import client


class Settings(application.Settings):
    junction_api_address: Sequence[str]
    junction_api_token: str
    flight_stats_api_address: Sequence[str]
    flight_stats_app_id: str
    flight_stats_app_key: str
    redis_dsn: Sequence[AnyUrl]
    mongo_dsn: Sequence[AnyUrl]
    mongo_db: str
    twilio_sid: str
    twilio_token: str
    twilio_sender: str
    validate_responses_against_spec: bool = True


def create_dependencies(  # noqa: WPS211
    junction_client: client.Client,
    redis_client: redis.Client[str],
    fs_client: flight_stats_client.FlightStatusClient,
    twilio_client: twilio.TwilioClient,
    orders_repository: repository.OrdersRepository,
    subscriptions_repository: repository.SubscriptionsRepository,
    delay_webhook_repository: repository.DelayWebhookRepository,
) -> lagom.Container:
    container = lagom.Container()
    container[client.Client] = junction_client
    container[redis.Client[str]] = redis_client
    container[flight_stats_client.FlightStatusClient] = fs_client
    container[twilio.TwilioClient] = twilio_client
    container[repository.OrdersRepository] = orders_repository
    container[repository.SubscriptionsRepository] = subscriptions_repository
    container[repository.DelayWebhookRepository] = delay_webhook_repository
    return container
