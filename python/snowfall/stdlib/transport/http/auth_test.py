import asyncio

import httpx
import pytest
import pytest_httpx

from snowfall.stdlib.transport.http import auth


class TestTemporaryTokenAuth(object):
    async def test_unset_token_raised_error(self) -> None:
        token_auth = auth.TemporaryTokenAuth()
        client = httpx.AsyncClient(auth=token_auth)

        with pytest.raises(auth.TemporaryTokenNotSetError):
            await client.get(url="http://localhost")

    async def test_temporary_changes_token(
        self,
        httpx_mock: pytest_httpx.HTTPXMock,
    ) -> None:
        httpx_mock.add_response()
        token_auth = auth.TemporaryTokenAuth()
        client = httpx.AsyncClient(auth=token_auth)

        with token_auth.temporary("bar"):
            response = await client.get(url="http://localhost")

        assert response.request.headers["Authorization"].endswith("bar")

    async def test_temporary_restores_token(
        self,
        httpx_mock: pytest_httpx.HTTPXMock,
    ) -> None:
        httpx_mock.add_response()
        token_auth = auth.TemporaryTokenAuth()
        client = httpx.AsyncClient(auth=token_auth)

        with token_auth.temporary("bar"):
            await client.get(url="http://localhost")

        with pytest.raises(auth.TemporaryTokenNotSetError):
            await client.get(url="http://localhost")

    async def test_temporary_token_is_not_overwritten_in_context(
        self,
        httpx_mock: pytest_httpx.HTTPXMock,
    ) -> None:
        httpx_mock.add_response()
        token_auth = auth.TemporaryTokenAuth()
        client = httpx.AsyncClient(auth=token_auth)

        tasks = [
            _make_request_with_temporary_token(client, token_auth, str(token))
            for token in range(2)
        ]

        await asyncio.gather(*tasks)


async def _make_request_with_temporary_token(
    client: httpx.AsyncClient,
    token_auth: auth.TemporaryTokenAuth,
    token: str,
) -> None:
    async def wrapper() -> None:
        await asyncio.sleep(0.1)
        response = await client.get(url="http://localhost")
        authorization = response.request.headers["Authorization"]
        assert authorization.endswith(
            token,
        ), "Did not find expected token {0} in {1}".format(token, authorization)

    with token_auth.temporary(token):
        await wrapper()
