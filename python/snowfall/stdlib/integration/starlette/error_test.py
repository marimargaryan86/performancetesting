import http

import httpx
from starlette import applications, requests, responses, status

_NOT_FOUND_PATH = "/not-found"
_UNHANDLED_ERROR_PATH = "/validation"


async def test_not_found_content_type(test_client: httpx.AsyncClient) -> None:
    response = await test_client.get(_NOT_FOUND_PATH)
    assert response.headers["content-type"] == "application/vnd.api+json"


async def test_not_found_status_code(test_client: httpx.AsyncClient) -> None:
    response = await test_client.get(_NOT_FOUND_PATH)
    assert response.status_code == status.HTTP_404_NOT_FOUND


async def test_not_found_format(test_client: httpx.AsyncClient) -> None:
    response = await test_client.get(_NOT_FOUND_PATH)
    status_code = http.HTTPStatus(status.HTTP_404_NOT_FOUND)

    for error in response.json()["errors"]:
        assert error["status"] == str(status.HTTP_404_NOT_FOUND)
        assert error["title"] == status_code.phrase
        assert error["detail"] == status_code.description


async def _error_endpoint(request: requests.Request) -> responses.Response:
    raise RuntimeError("Unhandled exception")


async def test_unhandled_error_content_type(
    test_app: applications.Starlette,
    test_client: httpx.AsyncClient,
) -> None:
    test_app.add_route(_UNHANDLED_ERROR_PATH, _error_endpoint)
    response = await test_client.get(_UNHANDLED_ERROR_PATH)
    assert response.headers["content-type"] == "application/vnd.api+json"


async def test_unhandled_error_status_code(
    test_app: applications.Starlette,
    test_client: httpx.AsyncClient,
) -> None:
    test_app.add_route(_UNHANDLED_ERROR_PATH, _error_endpoint)
    response = await test_client.get(_UNHANDLED_ERROR_PATH)
    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR


async def test_unhandled_error_format(
    test_app: applications.Starlette,
    test_client: httpx.AsyncClient,
) -> None:
    test_app.add_route(_UNHANDLED_ERROR_PATH, _error_endpoint)
    response = await test_client.get(_UNHANDLED_ERROR_PATH)
    status_code = http.HTTPStatus(status.HTTP_500_INTERNAL_SERVER_ERROR)

    for error in response.json()["errors"]:
        assert error["status"] == str(status.HTTP_500_INTERNAL_SERVER_ERROR)
        assert error["title"] == status_code.phrase
        assert error["detail"] == status_code.description
