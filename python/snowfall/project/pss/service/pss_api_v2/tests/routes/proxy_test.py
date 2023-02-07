import json
from unittest.mock import create_autospec

from fastapi import status
from fastapi.responses import Response
from fastapi.testclient import TestClient

from snowfall.project.pss.service.pss_api_v2.services.proxy import ProxyService


def test_proxy_endpoint_returns_correct_json_response(client: TestClient) -> None:
    mocked_proxy_service = create_autospec(ProxyService, spec_set=True, instance=True)
    response = Response(
        content=json.dumps({"message": "hello"}),
        status_code=status.HTTP_200_OK,
        headers={
            "Content-Type": "application/json",
            "other_header": "other_header_value",
        },
    )
    mocked_proxy_service.proxy_request.return_value = response

    client.app.dependency_overrides[  # type: ignore[attr-defined]
        ProxyService
    ] = lambda: mocked_proxy_service

    resp = client.get("/a-fake-endpoint")
    resp_json = resp.json()

    assert resp.status_code == status.HTTP_200_OK
    assert resp.headers["Content-Type"] == "application/json"
    assert resp_json == {"message": "hello"}
