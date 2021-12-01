import dataclasses
import http

from starlette import exceptions, requests, responses


@dataclasses.dataclass
class JsonApiError(object):
    status: str
    title: str
    detail: str


class JsonApiResponse(responses.JSONResponse):
    media_type = "application/vnd.api+json"


async def exception_handler(
    request: requests.Request,
    exc: exceptions.HTTPException,
) -> responses.JSONResponse:
    status = http.HTTPStatus(exc.status_code or http.HTTPStatus.INTERNAL_SERVER_ERROR)

    return JsonApiResponse(
        {
            "errors": [
                dataclasses.asdict(
                    JsonApiError(
                        status=str(int(status)),
                        title=status.phrase,
                        detail=status.description,
                    ),
                ),
            ],
        },
        status_code=status,
    )
