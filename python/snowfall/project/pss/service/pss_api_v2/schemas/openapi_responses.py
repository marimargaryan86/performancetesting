from typing import Any

from snowfall.project.pss.service.pss_api_v2.schemas.responses import (
    ErrorResponseSchema,
)

forbidden_not_found_responses: dict[int | str, dict[str, Any]] = {
    403: {"model": ErrorResponseSchema},
    404: {"model": ErrorResponseSchema},
}

unauthorized_response: dict[int | str, dict[str, Any]] = {
    401: {"model": ErrorResponseSchema},
}

not_found_response: dict[int | str, dict[str, Any]] = {
    404: {"model": ErrorResponseSchema},
}

bad_request_response: dict[int | str, dict[str, Any]] = {
    400: {"model": ErrorResponseSchema},
}
