import httpx
from starlette import applications, requests, responses

_VALIDATION_PATH = "/validation"


class TestValidationMiddleware(object):
    async def test_openapi_defaults_are_applied(
        self,
        test_app_without_response_validation: applications.Starlette,
        test_client_without_response_validation: httpx.AsyncClient,
    ) -> None:
        test_app_without_response_validation.add_route(
            _VALIDATION_PATH,
            self._assert_defaults_are_applied,
        )
        await test_client_without_response_validation.get(_VALIDATION_PATH)

    async def _assert_defaults_are_applied(
        self,
        request: requests.Request,
    ) -> responses.Response:
        assert request.scope["parsed_query_string"].get("defaultBoolean")

        return responses.Response()
