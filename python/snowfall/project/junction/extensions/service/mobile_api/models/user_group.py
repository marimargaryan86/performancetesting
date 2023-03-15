from typing import Optional

import pydantic

from snowfall.stdlib import string


class UserGroup(pydantic.BaseModel):
    name: Optional[str]

    class Config(object):
        alias_generator = string.to_lower_camel
        allow_population_by_field_name = True
