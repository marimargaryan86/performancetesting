import pytest
from starlette import applications, middleware
from starlette.middleware import authentication as auth_middleware

from snowfall.project.junction.hub.service.hub_api import router
from snowfall.stdlib import authentication as stdlib_auth
from snowfall.stdlib.integration.starlette import application, authentication, handlers
from snowfall.stdlib.persistence import filesystem


async def mock_cookie_to_user(cookie: str) -> stdlib_auth.User:
    return stdlib_auth.User(identifier="foo", email="foo@example.com")


def _create_app() -> applications.Starlette:
    return application.create_starlette_app(
        routes=router.get_routes(),
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
def app() -> applications.Starlette:
    return _create_app()
