from pydantic.fields import Field
from pydantic.main import BaseModel


class CountrySchema(BaseModel):
    id_: int = Field(alias="id")
    code: str
    name: str
    label: str

    class Config(object):
        orm_mode = True
        allow_population_by_field_name = True
