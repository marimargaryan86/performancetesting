from pydantic.fields import Field

from snowfall.project.pss.service.pss_api_v2.schemas.schema import BaseSchema


class AccountResponseSchema(BaseSchema):
    id_: int = Field(alias="id")
    email: str
    firstname: str
    lastname: str
