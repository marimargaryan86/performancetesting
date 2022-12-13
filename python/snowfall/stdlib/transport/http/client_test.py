import http
import inspect

import httpx
import pytest
import pytest_httpx

from snowfall.stdlib.transport.http import client, errors


async def test_http_status_error(
    httpx_mock: pytest_httpx.HTTPXMock,
    http_client: client.HttpClient,
) -> None:
    httpx_mock.add_response(
        url="https://test_url/hello?a=24",
        status_code=400,
        json={
            "status": 400,
            "message": "Bad request",
        },
    )

    with pytest.raises(errors.HttpStatusError) as status_exc:
        await http_client._make_request(  # noqa: WPS437
            client.RequestOptions(method="GET", path="/hello", query={"a": "24"}),
        )

        assert str(status_exc.value.body["message"]) == "Bad request"


async def test_empty_title_error_message(
    httpx_mock: pytest_httpx.HTTPXMock,
    http_client: client.HttpClient,
) -> None:
    status = http.HTTPStatus(http.HTTPStatus.BAD_REQUEST)
    httpx_mock.add_response(
        url="https://test_url/hello",
        status_code=400,
    )

    with pytest.raises(errors.HttpStatusError) as status_exc:
        await http_client._make_request(  # noqa: WPS437
            client.RequestOptions(method="POST", path="/hello", payload={"a": 24}),
        )

        assert str(status_exc.value) == status.description


async def test_default_error_message(
    httpx_mock: pytest_httpx.HTTPXMock,
    http_client: client.HttpClient,
) -> None:
    httpx_mock.add_exception(
        url="https://test_url/hello",
        exception=httpx.ConnectError(""),
    )

    with pytest.raises(errors.RequestError) as exc_info:
        await http_client._make_request(  # noqa: WPS437
            client.RequestOptions(
                method="PATCH",
                path="/hello",
                headers={"Content-Type": "application/json"},
            ),
        )

        assert str(exc_info.value) == inspect.getdoc(httpx.ConnectError)


async def test_timeout_error_message(
    httpx_mock: pytest_httpx.HTTPXMock,
    http_client: client.HttpClient,
) -> None:
    httpx_mock.add_exception(
        url="https://test_url/hello",
        exception=httpx.ReadTimeout(""),
    )

    with pytest.raises(errors.TimeOutError) as exc_info:
        await http_client._make_request(  # noqa: WPS437
            client.RequestOptions(method="DELETE", path="/hello"),
        )

        assert str(exc_info.value) == inspect.getdoc(httpx.ReadTimeout)
