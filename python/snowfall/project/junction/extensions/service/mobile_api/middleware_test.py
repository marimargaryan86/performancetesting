import base64
from collections.abc import Mapping

import pytest
from starlette import authentication, requests

from snowfall.project.junction.extensions.service.mobile_api import conftest, middleware


@pytest.fixture()
def auth_backend() -> middleware.AuthenticationBackend:
    return middleware.AuthenticationBackend(
        public_key=base64.b64decode(conftest.jwt_public_key).decode(),
        token_version=conftest.jwt_token_version,
    )


async def test_missing_security_method_is_skipped(
    auth_backend: middleware.AuthenticationBackend,
) -> None:
    conn = requests.HTTPConnection(
        scope={
            "type": "http",
            "security": {},
        },
    )

    assert await auth_backend.authenticate(conn) is None


@pytest.mark.parametrize(
    "security",
    [
        {"otp": ""},
        {"jwt": ""},
    ],
)
async def test_empty_security_method_fails(
    auth_backend: middleware.AuthenticationBackend,
    security: Mapping[str, str],
) -> None:
    conn = requests.HTTPConnection(
        scope={
            "type": "http",
            "security": security,
        },
    )

    with pytest.raises(authentication.AuthenticationError):
        await auth_backend.authenticate(conn)
