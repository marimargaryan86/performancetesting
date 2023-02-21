from typing import Any, Dict

from snowfall.project.pss.service.pss_api_v2.schemas.errors import ErrorMessageSchema

login_responses: Dict[int | str, Dict[str, Any]] = {
    403: {"model": ErrorMessageSchema},
    404: {"model": ErrorMessageSchema},
}

forgot_password_responses: Dict[int | str, Dict[str, Any]] = {
    404: {"model": ErrorMessageSchema},
}
