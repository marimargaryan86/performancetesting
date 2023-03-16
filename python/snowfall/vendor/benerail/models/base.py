from pydantic import BaseModel

from snowfall.stdlib import string


class BenerailBaseModel(BaseModel):
    class Config(object):
        allow_population_by_field_name = True
        alias_generator = string.to_lower_camel
