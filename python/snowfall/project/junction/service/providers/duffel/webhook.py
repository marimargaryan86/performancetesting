import ipaddress

import lagom
from lagom.integrations import starlette
from starlette import endpoints, requests, responses, routing, status
from starlette.middleware import Middleware

from snowfall.project.junction.service.providers.duffel import (
    middlewares,
    signature_validator,
)
from snowfall.stdlib.integration.starlette import application as starlette_application
from snowfall.stdlib.service import application


class WebhookSettings(starlette_application.Settings):
    http_address: ipaddress.IPv4Address = ipaddress.IPv4Address("127.0.0.1")
    http_port: int = 8003
    webhook_secret: str = ""


def create_dependencies() -> lagom.Container:
    return lagom.Container()


class AirlineInitiatedOrderChanges(endpoints.HTTPEndpoint):
    async def post(  # noqa: WPS231
        self,
        request: requests.Request,
    ) -> responses.Response:
        return responses.Response(status_code=status.HTTP_204_NO_CONTENT)


def get_routes(
    dependencies: lagom.Container,
) -> list[routing.BaseRoute]:
    integration = starlette.StarletteIntegration(dependencies)
    return [
        integration.route(
            "/airline-initiated-order-changes",
            AirlineInitiatedOrderChanges,
            name="Webhooks",
        ),
    ]


async def serve(
    app: application.Application[WebhookSettings],
) -> None:
    asgi_app = starlette_application.create_starlette_app(
        routes=get_routes(create_dependencies()),
        custom_middlewares=[
            Middleware(
                middlewares.SignatureValidationMiddleware,
                validator=signature_validator.WebhookSignatureValidator(
                    secret=app.settings.webhook_secret,
                ),
            ),
        ],
        openapi_path=None,
    )

    await starlette_application.serve(
        starlette_app=asgi_app,
        settings=app.settings,
    )
