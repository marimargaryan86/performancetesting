from pydantic.v1 import BaseModel

from snowfall.stdlib import string


class BenerailBaseModel(BaseModel):
    class Config:
        allow_population_by_field_name = True
        alias_generator = string.to_lower_camel
        use_enum_values = True
