from typing import Any, Dict

from snowfall.project.pss.service.pss_api_v2.schemas.responses import (
    ErrorResponseSchema,
)

forbidden_not_found_responses: Dict[int | str, Dict[str, Any]] = {
    403: {"model": ErrorResponseSchema},
    404: {"model": ErrorResponseSchema},
}

unauthorized_response: Dict[int | str, Dict[str, Any]] = {
    401: {"model": ErrorResponseSchema},
}

not_found_response: Dict[int | str, Dict[str, Any]] = {
    404: {"model": ErrorResponseSchema},
}

bad_request_response: Dict[int | str, Dict[str, Any]] = {
    400: {"model": ErrorResponseSchema},
}
