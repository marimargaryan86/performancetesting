from pydantic import v1 as pydantic

from snowfall.stdlib import string


class UserGroup(pydantic.BaseModel):
    name: str | None

    class Config(object):
        alias_generator = string.to_lower_camel
        allow_population_by_field_name = True
