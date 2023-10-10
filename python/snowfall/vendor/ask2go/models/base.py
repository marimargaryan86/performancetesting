import pydantic

from snowfall.stdlib import string
from snowfall.stdlib.integration.pydantic import model


class CamelCaseBaseModel(model.DefaultingBaseModel):
    model_config = pydantic.ConfigDict(
        alias_generator=string.to_lower_camel,
        populate_by_name=True,
        coerce_numbers_to_str=True,
    )
