import http
import inspect

import httpx
import pytest
import pytest_httpx

from snowfall.vendor.ask2go import client, errors

_URL = "https://test_url/api/Airports"


@pytest.mark.asyncio
async def test_error_message(
    httpx_mock: pytest_httpx.HTTPXMock,
    ask2go_client: client.Ask2GoClient,
) -> None:
    expected_title = "foo is not in the correct format"
    httpx_mock.add_response(
        url=_URL,
        status_code=400,
        json={
            "title": expected_title,
            "status": 400,
            "instance": "urn:ask2go:error:0cb6104b-57bc-460a-a931-dd40f3ca7f6d",
        },
    )

    with pytest.raises(errors.ServiceError) as excinfo:
        await ask2go_client.get_airports()

    assert str(excinfo.value) == "400: {0}".format(expected_title)  # noqa: WPS441


@pytest.mark.asyncio
async def test_empty_title_error_message(
    httpx_mock: pytest_httpx.HTTPXMock,
    ask2go_client: client.Ask2GoClient,
) -> None:

    status = http.HTTPStatus(http.HTTPStatus.BAD_REQUEST)
    expected_title = "{0}: {1}".format(status.value, status.description)
    httpx_mock.add_response(
        url=_URL,
        status_code=status.value,
        json={
            "title": "",
            "status": status.value,
            "instance": "urn:ask2go:error:0cb6104b-57bc-460a-a931-dd40f3ca7f6d",
        },
    )

    with pytest.raises(errors.ServiceError) as excinfo:
        await ask2go_client.get_airports()

    assert str(excinfo.value) == expected_title  # noqa: WPS441


@pytest.mark.asyncio
async def test_critical_error_message(
    httpx_mock: pytest_httpx.HTTPXMock,
    ask2go_client: client.Ask2GoClient,
) -> None:
    status = http.HTTPStatus(http.HTTPStatus.INTERNAL_SERVER_ERROR)
    expected_title = "{0}: {1}".format(status.value, status.description)
    httpx_mock.add_response(url=_URL, status_code=status.value)

    with pytest.raises(errors.ServiceError) as excinfo:
        await ask2go_client.get_airports()

    assert str(excinfo.value) == expected_title  # noqa: WPS441


@pytest.mark.asyncio
async def test_bad_json_error_message(
    httpx_mock: pytest_httpx.HTTPXMock,
    ask2go_client: client.Ask2GoClient,
) -> None:
    status = http.HTTPStatus(http.HTTPStatus.BAD_GATEWAY)
    expected_title = "{0}: {1}".format(status.value, status.description)
    httpx_mock.add_response(url=_URL, status_code=status.value, json=[])

    with pytest.raises(errors.ServiceError) as excinfo:
        await ask2go_client.get_airports()

    assert str(excinfo.value) == expected_title  # noqa: WPS441


@pytest.mark.asyncio
async def test_default_error_message(
    httpx_mock: pytest_httpx.HTTPXMock,
    ask2go_client: client.Ask2GoClient,
) -> None:
    httpx_mock.add_exception(url=_URL, exception=httpx.ReadTimeout(""))

    with pytest.raises(errors.ServiceError) as excinfo:
        await ask2go_client.get_airports()

    assert str(excinfo.value) == inspect.getdoc(httpx.ReadTimeout)  # noqa: WPS441
