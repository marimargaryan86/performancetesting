from starlette import requests

from snowfall.stdlib import authentication as stdlib_auth
from snowfall.stdlib.integration.starlette import authentication


async def mock_cookie_to_user(cookie: str) -> stdlib_auth.User:
    return stdlib_auth.User(identifier="foo", email="foo@example.com")


async def test_missing_cookie_is_skipped() -> None:
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


async def test_cookie_gives_user() -> None:
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
