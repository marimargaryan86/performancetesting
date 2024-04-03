import pytest
from starlette import authentication as starlette_auth
from starlette import requests

from snowfall.stdlib import authentication as stdlib_auth
from snowfall.stdlib.integration.starlette import authentication


async def mock_cookie_to_user(cookie: str) -> stdlib_auth.User:
    return stdlib_auth.User(identifier="foo", email="foo@example.com")


async def mock_jwt_to_user_id(jwt: str) -> str:
    return "foo"


class TestCookieAuth:
    async def test_missing_cookie_is_skipped(self) -> None:
        auth = authentication.CookieAuthenticationBackend(
            cookie_to_user=mock_cookie_to_user,
        )
        conn = requests.HTTPConnection(
            scope={
                "type": "http",
                "security": {},
            },
        )

        assert await auth.authenticate(conn) is None

    async def test_empty_cookie_fails(self) -> None:
        auth = authentication.CookieAuthenticationBackend(
            cookie_to_user=mock_cookie_to_user,
        )
        conn = requests.HTTPConnection(
            scope={
                "type": "http",
                "security": {"cookie": ""},
            },
        )

        with pytest.raises(starlette_auth.AuthenticationError):
            await auth.authenticate(conn)

    async def test_cookie_gives_user(self) -> None:
        auth = authentication.CookieAuthenticationBackend(
            cookie_to_user=mock_cookie_to_user,
        )
        conn = requests.HTTPConnection(
            scope={
                "type": "http",
                "security": {
                    "cookie": "foo",
                },
            },
        )

        assert await auth.authenticate(conn)


class TestJWTAuth:
    async def test_missing_jwt_is_skipped(self) -> None:
        auth = authentication.JWTAuthenticationBackend(
            jwt_to_user_id=mock_jwt_to_user_id,
        )
        conn = requests.HTTPConnection(
            scope={
                "type": "http",
                "security": {},
            },
        )

        assert await auth.authenticate(conn) is None

    async def test_empty_jwt_fails(self) -> None:
        auth = authentication.JWTAuthenticationBackend(
            jwt_to_user_id=mock_jwt_to_user_id,
        )
        conn = requests.HTTPConnection(
            scope={
                "type": "http",
                "security": {"jwt": ""},
            },
        )

        with pytest.raises(starlette_auth.AuthenticationError):
            await auth.authenticate(conn)

    async def test_jwt_gives_user(self) -> None:
        auth = authentication.JWTAuthenticationBackend(
            jwt_to_user_id=mock_jwt_to_user_id,
        )
        conn = requests.HTTPConnection(
            scope={
                "type": "http",
                "security": {
                    "jwt": "foo",
                },
            },
        )

        assert await auth.authenticate(conn)
