from typing import Any, Dict

from snowfall.project.pss.service.pss_api_v2.schemas.errors import ErrorMessage

login_responses: Dict[int | str, Dict[str, Any]] = {
    403: {"model": ErrorMessage},
    404: {"model": ErrorMessage},
}
