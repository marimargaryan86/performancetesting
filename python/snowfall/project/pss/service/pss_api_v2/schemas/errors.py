from snowfall.project.pss.service.pss_api_v2.schemas.schema import BaseSchema

FAIL = "fail"


class ErrorMessage(BaseSchema):
    status: str = FAIL
    message: str
