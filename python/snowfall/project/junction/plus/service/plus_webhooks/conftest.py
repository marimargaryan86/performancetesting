import datetime
from collections.abc import AsyncIterator, Mapping

import httpx
import pytest
from fakeredis import aioredis as fakeredis
from starlette import applications
from starlette.middleware import Middleware
from twilio.request_validator import RequestValidator

from snowfall.project.junction.plus.adapter import configuration_vectors
from snowfall.project.junction.plus.adapter import (
    monitoring_rules as monitoring_rules_adapter,
)
from snowfall.project.junction.plus.adapter import (
    notification_event_publisher as notification_event_publisher_adapter,
)
from snowfall.project.junction.plus.adapter import (
    subscribers as subscribers_adapter,
)
from snowfall.project.junction.plus.service.notifications.v1alpha import (
    models_pb2 as notifications_models_pb2,
)
from snowfall.project.junction.plus.service.plus_webhooks import (
    bootstrap,
    middlewares,
    state,
)
from snowfall.project.junction.plus.service.plus_webhooks.routes import router
from snowfall.stdlib.integration.starlette import application
from snowfall.stdlib.persistence.redis import types as redis
from snowfall.stdlib.v1 import phone_number_pb2


@pytest.fixture()
def secret_key() -> str:
    return "Very-Secret-Key"


@pytest.fixture()
def cirium_flex_alert_key() -> str:
    return "MQ|3424|ORD|CLE|ARRIVAL_DELAY|2020-04-07T16:16:39.388Z"


@pytest.fixture()
def whatsapp_body() -> Mapping[str, str]:
    return {
        "Body": "Test body",
        "From": "whatsapp:9900000002",
        "To": "whatsapp:9900000001",
    }


@pytest.fixture()
def whatsapp_body_hash(
    whatsapp_body: Mapping[str, str],
    twilio_validator: RequestValidator,
) -> str:
    return twilio_validator.compute_signature(  # type: ignore[no-untyped-call]
        "https://example.com/webhooks/whatsapp",
        whatsapp_body,
    )


@pytest.fixture()
def cirium_flex_alert_hash(cirium_flex_alert_key: str, secret_key: str) -> str:
    return middlewares.calculate_hash(
        cirium_flex_alert_key.encode(),
        secret_key.encode(),
    )


@pytest.fixture()
def twilio_validator(secret_key: str) -> RequestValidator:
    return RequestValidator(secret_key)


@pytest.fixture()
def monitoring_rules_client() -> monitoring_rules_adapter.Client:
    return monitoring_rules_adapter.DictClient(
        [
            notifications_models_pb2.MonitoringRule(
                id="monitoring_rule_1",
                subscriber_ids=["1"],
            ),
        ],
    )


@pytest.fixture()
def subscribers_client() -> subscribers_adapter.Client:
    return subscribers_adapter.DictClient(
        [
            notifications_models_pb2.Subscriber(
                id="1",
            ),
        ],
    )


@pytest.fixture()
def configuration_vectors_client() -> configuration_vectors.Client:
    return configuration_vectors.DictClient(
        [
            notifications_models_pb2.ConfigurationVector(
                id="1",
                reseller_id="1",
                mobile_phone=phone_number_pb2.PhoneNumber(
                    e164_number="9900000001",
                ),
            ),
        ],
    )


@pytest.fixture()
def notification_event_publisher_client() -> (
    notification_event_publisher_adapter.Client
):
    return notification_event_publisher_adapter.DictClient()


@pytest.fixture()
def redis_client(redis_client: fakeredis.FakeRedis) -> redis.Client[str]:
    return redis.Client(
        redis_client,
        prefix="plus_webhooks",
    )


@pytest.fixture()
def app(  # noqa: WPS211
    secret_key: str,
    monitoring_rules_client: monitoring_rules_adapter.Client,
    subscribers_client: subscribers_adapter.Client,
    configuration_vectors_client: configuration_vectors.Client,
    notification_event_publisher_client: notification_event_publisher_adapter.Client,
    twilio_validator: RequestValidator,
    redis_client: redis.Client[str],
) -> applications.Starlette:
    return application.create_starlette_app(
        custom_middlewares=[
            Middleware(
                middlewares.HmacHeaderMiddleware,
                secret_key=secret_key,
                twilio_validator=twilio_validator,
            ),
        ],
        routes=router.get_routes(
            bootstrap.create_dependencies(
                monitoring_rules_client=monitoring_rules_client,
                subscribers_client=subscribers_client,
                configuration_vectors_client=configuration_vectors_client,
                notification_event_publisher_client=notification_event_publisher_client,
                subscribers_state=state.SubscriberState(
                    redis_client=redis_client,
                    cache_ttl=datetime.timedelta(minutes=10),
                ),
            ),
        ),
        openapi_path=None,
    )


@pytest.fixture()
async def client(
    app: applications.Starlette,
) -> AsyncIterator[httpx.AsyncClient]:
    async with httpx.AsyncClient(app=app, base_url="https://example.com") as client:
        yield client
