import datetime
import functools

import pydantic

from snowfall.stdlib import string


class CamelCaseBaseModel(pydantic.BaseModel):
    class Config(object):
        alias_generator = string.to_lower_camel
        allow_population_by_field_name = True
        keep_untouched = (functools.cached_property,)

        json_encoders = {
            datetime.datetime: lambda datetime_object: datetime_object.isoformat(
                timespec="seconds",
            ),
        }
