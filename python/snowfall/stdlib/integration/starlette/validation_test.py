import http

import httpx
from starlette import applications, requests, responses, status

from snowfall.stdlib.integration.starlette import models

_VALIDATION_PATH = "/validation"


async def _failed_validation(request: requests.Request) -> responses.Response:
    return models.JsonApiResponse(
        models.Body(data=models.ResourceIdentifier(id="1", type="failed")),
    )


async def _success_validation(request: requests.Request) -> responses.Response:
    return models.JsonApiResponse(
        models.Body(data=models.ResourceIdentifier(id="1", type="success")),
    )


async def _request_validation(request: requests.Request) -> responses.Response:
    return responses.Response(status_code=status.HTTP_204_NO_CONTENT)


class TestResponseValidation(object):
    async def test_response_validation_failure_status_code(
        self,
        test_app: applications.Starlette,
        test_client: httpx.AsyncClient,
    ) -> None:
        test_app.add_route(_VALIDATION_PATH, _failed_validation)
        response = await test_client.get(_VALIDATION_PATH)
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR

    async def test_response_validation_failure_response(
        self,
        test_app: applications.Starlette,
        test_client: httpx.AsyncClient,
    ) -> None:
        test_app.add_route(_VALIDATION_PATH, _failed_validation)
        response = await test_client.get(_VALIDATION_PATH)
        status_code = http.HTTPStatus(status.HTTP_500_INTERNAL_SERVER_ERROR)

        for error in response.json()["errors"]:
            assert error["status"] == str(status.HTTP_500_INTERNAL_SERVER_ERROR)
            assert error["title"] == status_code.phrase
            assert error["detail"] == status_code.description

    async def test_no_response_validation(
        self,
        test_app_without_response_validation: applications.Starlette,
        test_client_without_response_validation: httpx.AsyncClient,
    ) -> None:
        test_app_without_response_validation.add_route(
            _VALIDATION_PATH,
            _failed_validation,
        )
        response = await test_client_without_response_validation.get(_VALIDATION_PATH)
        assert response.status_code == status.HTTP_200_OK

    async def test_response_validation_success_status_code(
        self,
        test_app: applications.Starlette,
        test_client: httpx.AsyncClient,
    ) -> None:
        test_app.add_route(_VALIDATION_PATH, _success_validation)
        response = await test_client.get(_VALIDATION_PATH)
        assert response.status_code == status.HTTP_200_OK


class TestRequestValidation(object):
    async def test_request_validation_failure_status_code(
        self,
        test_app: applications.Starlette,
        test_client: httpx.AsyncClient,
    ) -> None:
        test_app.add_route(_VALIDATION_PATH, _request_validation, methods=["POST"])
        response = await test_client.post(
            _VALIDATION_PATH,
            json={"data": {"type": "failure"}},
            headers={"Content-Type": "application/vnd.api+json"},
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    async def test_request_validation_success_status_code(
        self,
        test_app: applications.Starlette,
        test_client: httpx.AsyncClient,
    ) -> None:
        test_app.add_route(_VALIDATION_PATH, _request_validation, methods=["POST"])
        response = await test_client.post(
            _VALIDATION_PATH,
            json={"data": {"type": "success"}},
            headers={"Content-Type": "application/vnd.api+json"},
        )
        assert response.status_code == status.HTTP_204_NO_CONTENT
