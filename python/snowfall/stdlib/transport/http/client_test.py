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

    with pytest.raises(errors.HttpStatusError) as exc:
        await http_client._make_request(  # noqa: SLF001
            client.RequestOptions(method="GET", path="/hello", query={"a": "24"}),
        )

    assert str(exc.value.body["message"]) == "Bad request"  # noqa: WPS441


async def test_empty_title_error_message(
    httpx_mock: pytest_httpx.HTTPXMock,
    http_client: client.HttpClient,
) -> None:
    status = http.HTTPStatus(http.HTTPStatus.BAD_REQUEST)
    httpx_mock.add_response(
        url="https://test_url/hello",
        status_code=400,
    )

    with pytest.raises(errors.HttpStatusError) as exc:
        await http_client._make_request(  # noqa: SLF001
            client.RequestOptions(method="POST", path="/hello", payload={"a": 24}),
        )

    assert str(exc.value) == status.description  # noqa: WPS441


async def test_default_error_message(
    httpx_mock: pytest_httpx.HTTPXMock,
    http_client: client.HttpClient,
) -> None:
    httpx_mock.add_exception(
        url="https://test_url/hello",
        exception=httpx.ConnectError(""),
    )

    with pytest.raises(errors.RequestError) as exc:
        await http_client._make_request(  # noqa: SLF001
            client.RequestOptions(
                method="PATCH",
                path="/hello",
                headers={"Content-Type": "application/json"},
            ),
        )

    assert str(exc.value) == inspect.getdoc(httpx.ConnectError)  # noqa: WPS441


async def test_timeout_error_message(
    httpx_mock: pytest_httpx.HTTPXMock,
    http_client: client.HttpClient,
) -> None:
    httpx_mock.add_exception(
        url="https://test_url/hello",
        exception=httpx.ReadTimeout(""),
    )

    with pytest.raises(errors.TimeOutError) as exc:
        await http_client._make_request(  # noqa: SLF001
            client.RequestOptions(method="DELETE", path="/hello"),
        )

    assert str(exc.value) == inspect.getdoc(httpx.ReadTimeout)  # noqa: WPS441


_BASE_URL = "https://test.com"
_BASE_URL_WITH_PATH = "https://test.com/base-path"
_BASE_URL_WITH_PATH_TRAILING_STASH = "https://test.com/base-path/"


@pytest.mark.parametrize(
    ("options", "expected_str", "base_url"),
    [
        (
            client.RequestOptions(
                method="GET",
                path="test-path",
            ),
            "https://test.com/test-path",
            _BASE_URL,
        ),
        (
            client.RequestOptions(
                method="GET",
                path="/test-path",
            ),
            "https://test.com/test-path",
            _BASE_URL,
        ),
        (
            client.RequestOptions(
                method="GET",
                path="test-path",
            ),
            "https://test.com/base-path/test-path",
            _BASE_URL_WITH_PATH,
        ),
        (
            client.RequestOptions(
                method="GET",
                path="/test-path",
            ),
            "https://test.com/test-path",
            _BASE_URL_WITH_PATH,
        ),
        (
            client.RequestOptions(
                method="GET",
                path="test-path",
            ),
            "https://test.com/base-path/test-path",
            _BASE_URL_WITH_PATH_TRAILING_STASH,
        ),
        (
            client.RequestOptions(
                method="GET",
                path="/test-path",
            ),
            "https://test.com/test-path",
            _BASE_URL_WITH_PATH_TRAILING_STASH,
        ),
    ],
)
async def test_url_for_options(
    options: client.RequestOptions,
    expected_str: str,
    base_url: str,
) -> None:
    assert str(client.url_for_options(base_url, options)) == expected_str
