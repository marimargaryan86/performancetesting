from collections.abc import AsyncIterator, Mapping

import httpx
import pytest
from starlette import applications
from starlette.middleware import Middleware
from twilio.request_validator import RequestValidator

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
)
from snowfall.project.junction.plus.service.plus_webhooks.routes import router
from snowfall.stdlib.integration.starlette import application


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
        "From": "FromAcc",
        "To": "ToAcc",
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
def notification_event_publisher_client() -> (
    notification_event_publisher_adapter.Client
):
    return notification_event_publisher_adapter.DictClient()


@pytest.fixture()
def app(
    secret_key: str,
    monitoring_rules_client: monitoring_rules_adapter.Client,
    subscribers_client: subscribers_adapter.Client,
    notification_event_publisher_client: notification_event_publisher_adapter.Client,
    twilio_validator: RequestValidator,
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
                notification_event_publisher_client=notification_event_publisher_client,
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
