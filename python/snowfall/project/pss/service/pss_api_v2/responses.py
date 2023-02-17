from fastapi.responses import JSONResponse

from snowfall.project.pss.service.pss_api_v2.schemas.errors import FAIL


class ErrorMessage(JSONResponse):
    def __init__(self, status_code: int, message: str):
        super().__init__(
            status_code=status_code,
            content={"status": FAIL, "message": message},
        )
