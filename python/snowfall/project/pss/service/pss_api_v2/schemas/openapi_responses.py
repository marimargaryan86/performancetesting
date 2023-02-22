from typing import Any, Dict

from snowfall.project.pss.service.pss_api_v2.schemas.responses import (
    ErrorResponseSchema,
)

login_responses: Dict[int | str, Dict[str, Any]] = {
    403: {"model": ErrorResponseSchema},
    404: {"model": ErrorResponseSchema},
}

forgot_password_responses: Dict[int | str, Dict[str, Any]] = {
    404: {"model": ErrorResponseSchema},
}

reset_password_responses: Dict[int | str, Dict[str, Any]] = {
    403: {"model": ErrorResponseSchema},
    404: {"model": ErrorResponseSchema},
}
