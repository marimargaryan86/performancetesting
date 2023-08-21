from collections.abc import AsyncIterator, Mapping

import httpx
import pytest
from starlette import applications, middleware
from starlette.middleware import authentication as auth_middleware

from snowfall.project.junction.go import fixtures
from snowfall.project.junction.go.adapter import errors, orders
from snowfall.project.junction.hub.service.hub_api import bootstrap, router
from snowfall.stdlib import authentication as stdlib_auth
from snowfall.stdlib.integration.starlette import application, authentication, handlers
from snowfall.stdlib.persistence import filesystem


async def mock_cookie_to_user(cookie: str) -> stdlib_auth.User:
    return stdlib_auth.User(identifier="foo", email="foo@example.com")


@pytest.fixture()
def headers() -> dict[str, str]:
    return {
        "Accept": "application/vnd.api+json",
        "Cookie": "ory_kratos_session='test_cookie_header'",
    }


@pytest.fixture()
def orders_client() -> orders.Client:
    return orders.DictClient(
        fixtures.get_journeys(),
        fixtures.get_bookings_cancellations(),
    )


def _create_app(orders_client: orders.Client) -> applications.Starlette:
    asgi_app = application.create_starlette_app(
        routes=router.get_routes(
            bootstrap.create_dependencies(
                orders_client=orders_client,
            ),
        ),
        openapi_path=filesystem.resource_path("junction.hub_api", "openapi.json"),
        custom_middlewares=[
            middleware.Middleware(
                auth_middleware.AuthenticationMiddleware,
                backend=authentication.CookieAuthenticationBackend(
                    cookie_to_user=mock_cookie_to_user,
                ),
                on_error=handlers.auth_error_handler,
            ),
        ],
        security_headers=False,
    )

    asgi_app.add_exception_handler(
        errors.NotFoundError,
        handlers.not_found_error_handler,
    )
    return asgi_app


@pytest.fixture()
async def client(
    app: applications.Starlette,
    headers: Mapping[str, str],
) -> AsyncIterator[httpx.AsyncClient]:
    async with httpx.AsyncClient(app=app, base_url="https://example.com") as client:
        client.headers.update(dict(headers))

        yield client


@pytest.fixture()
def app(orders_client: orders.Client) -> applications.Starlette:
    return _create_app(orders_client=orders_client)
