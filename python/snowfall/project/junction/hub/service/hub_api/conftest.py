import pytest
from starlette import applications, middleware
from starlette.middleware import authentication as auth_middleware

from snowfall.project.junction.go import fixtures
from snowfall.project.junction.go.adapter import orders
from snowfall.project.junction.hub.service.hub_api import bootstrap, router
from snowfall.stdlib import authentication as stdlib_auth
from snowfall.stdlib.integration.starlette import application, authentication, handlers
from snowfall.stdlib.persistence import filesystem


async def mock_cookie_to_user(cookie: str) -> stdlib_auth.User:
    return stdlib_auth.User(identifier="foo", email="foo@example.com")


@pytest.fixture()
def orders_client() -> orders.Client:
    return orders.DictClient(
        fixtures.get_journeys(),
        fixtures.get_bookings_cancellations(),
    )


def _create_app(orders_client: orders.Client) -> applications.Starlette:
    return application.create_starlette_app(
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


@pytest.fixture()
def app(orders_client: orders.Client) -> applications.Starlette:
    return _create_app(orders_client=orders_client)
