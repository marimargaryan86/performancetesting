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
        models.Body(
            data=models.Resource(
                id="1",
                type="success",
                attributes={
                    "array": ["foo", 1],
                    "firstNullable": None,
                    "secondNullable": {"foo": "bar"},
                },
            ),
        ),
    )


async def _request_validation(request: requests.Request) -> responses.Response:
    return responses.Response(status_code=status.HTTP_204_NO_CONTENT)


async def _error_source_success(request: requests.Request) -> responses.Response:
    return responses.JSONResponse(
        content={
            "errors": [
                {
                    "status": "400",
                    "detail": "foo",
                    "source": {
                        "pointer": "foo",
                    },
                },
            ],
        },
        status_code=400,
        media_type="application/vnd.api+json",
    )


async def _error_no_source_failure(request: requests.Request) -> responses.Response:
    return responses.JSONResponse(
        content={
            "errors": [
                {
                    "status": "400",
                    "detail": "foo",
                    "source": {},
                },
            ],
        },
        status_code=400,
        media_type="application/vnd.api+json",
    )


async def _error_many_source_failure(request: requests.Request) -> responses.Response:
    return responses.JSONResponse(
        content={
            "errors": [
                {
                    "status": "400",
                    "detail": "foo",
                    "source": {
                        "pointer": "foo",
                        "header": "foo",
                    },
                },
            ],
        },
        status_code=400,
        media_type="application/vnd.api+json",
    )


class TestErrorValidation:
    async def test_error_source_validation_success(
        self,
        test_app: applications.Starlette,
        test_client: httpx.AsyncClient,
    ) -> None:
        test_app.add_route(_VALIDATION_PATH, _error_source_success)
        response = await test_client.get(_VALIDATION_PATH)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    async def test_error_multiple_source_validation_failure(
        self,
        test_app: applications.Starlette,
        test_client: httpx.AsyncClient,
    ) -> None:
        test_app.add_route(_VALIDATION_PATH, _error_many_source_failure)
        response = await test_client.get(_VALIDATION_PATH)
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR

    async def test_error_no_source_validation_failure(
        self,
        test_app: applications.Starlette,
        test_client: httpx.AsyncClient,
    ) -> None:
        test_app.add_route(_VALIDATION_PATH, _error_no_source_failure)
        response = await test_client.get(_VALIDATION_PATH)
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR


class TestResponseValidation:
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

    async def test_response_validation_success_status_code(
        self,
        test_app: applications.Starlette,
        test_client: httpx.AsyncClient,
    ) -> None:
        test_app.add_route(_VALIDATION_PATH, _success_validation)
        response = await test_client.get(_VALIDATION_PATH)
        assert response.status_code == status.HTTP_200_OK


class TestRequestValidation:
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
