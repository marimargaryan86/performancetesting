from pydantic.fields import Field

from snowfall.project.pss.service.pss_api_v2.schemas.schema import BaseSchema


class CountrySchema(BaseSchema):
    id_: int = Field(alias="id")
    code: str
    name: str
    label: str
