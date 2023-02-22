from typing import Any

from fastapi.responses import JSONResponse

from snowfall.project.pss.service.pss_api_v2.schemas.responses import FAIL, SUCCESS


class SuccessResponse(JSONResponse):
    def __init__(self, status_code: int, data: Any):  # noqa:WPS110
        super().__init__(
            status_code=status_code,
            content={"status": SUCCESS, "data": data},
        )


class ErrorResponse(JSONResponse):
    def __init__(self, status_code: int, message: str):
        super().__init__(
            status_code=status_code,
            content={"status": FAIL, "message": message},
        )
