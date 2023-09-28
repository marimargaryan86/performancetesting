from typing import Any

import aiofiles
import orjson
import pytest
import pytest_httpx

from snowfall.service.authentication import sessions
from snowfall.service.authentication.v1 import sessions_pb2
from snowfall.stdlib.persistence import filesystem
from snowfall.vendor.ory import client


async def _load_json_fixture(
    file_name: str,
) -> dict[str, Any]:
    file_path = filesystem.resource_path(
        package="snowfall.vendor.ory.client",
        resource="fixtures/{file_name}.json".format(
            file_name=file_name.removesuffix(".json"),
        ),
    )

    async with aiofiles.open(file_path) as file_handle:
        return orjson.loads(await file_handle.read())


@pytest.fixture()
def ory_client() -> client.OryClient:
    return client.OryClient(base_url="http://localhost")


@pytest.fixture()
def sessions_client(ory_client: client.OryClient) -> sessions.Sessions:
    return sessions.Sessions(ory_client=ory_client)


@pytest.fixture()
async def session_result(
    sessions_client: sessions.Sessions,
    httpx_mock: pytest_httpx.HTTPXMock,
) -> sessions_pb2.Session:
    httpx_mock.add_response(json=await _load_json_fixture("sessions_whoami"))

    return await sessions_client.get_session_for_cookie("foo")


@pytest.fixture()
async def session_result_no_metadata(
    sessions_client: sessions.Sessions,
    httpx_mock: pytest_httpx.HTTPXMock,
) -> sessions_pb2.Session:
    httpx_mock.add_response(
        json=await _load_json_fixture("sessions_whoami_no_metadata"),
    )

    return await sessions_client.get_session_for_cookie("foo")


async def test_unknown_cookie_raises_not_found(
    sessions_client: sessions.Sessions,
    httpx_mock: pytest_httpx.HTTPXMock,
) -> None:
    httpx_mock.add_response(status_code=404)

    with pytest.raises(sessions.NotFoundError):
        await sessions_client.get_session_for_cookie("foo")


async def test_unknown_error_is_raised(
    sessions_client: sessions.Sessions,
    httpx_mock: pytest_httpx.HTTPXMock,
) -> None:
    httpx_mock.add_response(status_code=500)

    with pytest.raises(sessions.UnknownError):
        await sessions_client.get_session_for_cookie("foo")


async def test_valid_cookie_gives_session(
    sessions_client: sessions.Sessions,
    httpx_mock: pytest_httpx.HTTPXMock,
) -> None:
    httpx_mock.add_response(json=await _load_json_fixture("sessions_whoami"))
    session = await sessions_client.get_session_for_cookie("foo")

    assert session.id


async def test_session_contains_metadata(session_result: sessions_pb2.Session) -> None:
    assert len(session_result.identity.metadata_public)


async def test_session_is_missing_metadata(
    session_result_no_metadata: sessions_pb2.Session,
) -> None:
    assert not len(session_result_no_metadata.identity.metadata_public)
