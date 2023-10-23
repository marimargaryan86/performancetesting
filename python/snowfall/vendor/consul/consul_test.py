import pytest_httpx

from snowfall.vendor.consul import client


async def test_get_key_returned(
    httpx_mock: pytest_httpx.HTTPXMock,
    consul_client: client.ConsulClient,
) -> None:
    consul_value = b"val1"
    httpx_mock.add_response(
        url="https://test_url/v1/kv/providers/reseller-providers?raw=true",
        status_code=200,
        content=consul_value,
    )

    value = await consul_client.get_key(
        "/providers/reseller-providers/",
    )

    assert value == consul_value


async def test_put_key_succeeded(
    httpx_mock: pytest_httpx.HTTPXMock,
    consul_client: client.ConsulClient,
) -> None:
    consul_value = b"val1"
    httpx_mock.add_response(
        url="https://test_url/v1/kv/providers/reseller-providers",
        status_code=200,
        content=b"true\n",
        headers={"Content-Type": ""},
    )

    value = await consul_client.put_key(
        "/providers/reseller-providers/",
        consul_value,
    )

    assert value
