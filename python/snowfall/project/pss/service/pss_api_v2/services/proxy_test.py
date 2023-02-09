from unittest.mock import create_autospec

import httpx
from fastapi import requests, status

from snowfall.project.pss.service.pss_api_v2.services.proxy import ProxyService


async def test_that_proxy_request_returns_original_endpoints_response() -> None:
    httpx_mock = create_autospec(httpx.AsyncClient, spec_set=True, instance=True)
    response = httpx.Response(
        status_code=status.HTTP_200_OK,
        content=b"Fake Content",
        headers={
            "fake_header": "fake_header_value",
            "Content-Type": "fake_content_type",
        },
    )
    httpx_mock.request.return_value = response
    request_mock = create_autospec(requests.Request, spec_set=True, instance=True)

    proxy_client = ProxyService(client=httpx_mock)
    resp = await proxy_client.proxy_request(request_mock)

    assert resp.status_code == status.HTTP_200_OK
    assert resp.body == b"Fake Content"
    assert resp.media_type == "fake_content_type"
