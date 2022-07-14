import datetime

import pydantic

from snowfall.stdlib import string


class CamelCaseBaseModel(pydantic.BaseModel):
    class Config(object):
        alias_generator = string.to_camel
        allow_population_by_field_name = True

        json_encoders = {
            datetime.datetime: lambda datetime_object: datetime_object.isoformat(
                timespec="seconds",
            ),
        }
