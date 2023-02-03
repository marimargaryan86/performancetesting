from pydantic.fields import Field

from snowfall.project.pss.service.api.schemas.schema import BaseSchema


class CountrySchema(BaseSchema):
    id_: int = Field(alias="id")
    code: str
    name: str
    label: str
