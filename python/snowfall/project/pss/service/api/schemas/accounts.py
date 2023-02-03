from pydantic.fields import Field

from snowfall.project.pss.service.api.schemas.schema import BaseSchema


class AccountResponseSchema(BaseSchema):
    id_: int = Field(alias="id")
    email: str
    firstname: str
    lastname: str
