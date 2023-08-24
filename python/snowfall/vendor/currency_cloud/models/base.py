from pydantic.v1 import BaseModel

from snowfall.stdlib import string


class CamelCaseBaseModel(BaseModel):
    class Config(object):
        alias_generator = string.to_lower_camel
        allow_population_by_field_name = True
        use_enum_values = True
