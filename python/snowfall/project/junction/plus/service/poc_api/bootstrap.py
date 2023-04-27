from typing import Sequence

import lagom
from pydantic import AnyUrl

from snowfall.project.junction.plus.service.poc_api import (
    flight_stats_client,
    icoupon,
    repository,
    s3,
    travel_fusion,
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
    icoupon_api_address: Sequence[str]
    icoupon_client_id: str
    icoupon_client_secret: str
    aws_access_key: str
    aws_secret_key: str
    redis_dsn: Sequence[AnyUrl]
    mongo_dsn: Sequence[AnyUrl]
    mongo_db: str
    twilio_sid: str
    twilio_token: str
    twilio_sender: str
    tf_api_address: Sequence[str]
    tf_client_key: str
    validate_responses_against_spec: bool = True


def create_dependencies(  # noqa: WPS211
    junction_client: client.Client,
    redis_client: redis.Client[str],
    fs_client: flight_stats_client.FlightStatusClient,
    icoupon_client: icoupon.ICouponClient,
    twilio_client: twilio.TwilioClient,
    s3_client: s3.S3Client,
    tf_client: travel_fusion.TravelFusionClient,
    orders_repository: repository.OrdersRepository,
    subscriptions_repository: repository.SubscriptionsRepository,
    delay_webhook_repository: repository.DelayWebhookRepository,
) -> lagom.Container:
    container = lagom.Container()
    container[client.Client] = junction_client
    container[redis.Client[str]] = redis_client
    container[flight_stats_client.FlightStatusClient] = fs_client
    container[icoupon.ICouponClient] = icoupon_client
    container[twilio.TwilioClient] = twilio_client
    container[travel_fusion.TravelFusionClient] = tf_client
    container[s3.S3Client] = s3_client
    container[repository.OrdersRepository] = orders_repository
    container[repository.SubscriptionsRepository] = subscriptions_repository
    container[repository.DelayWebhookRepository] = delay_webhook_repository
    return container
