from pydantic import BaseModel as PydanticBase
from pydantic import ConfigDict, alias_generators


class BaseModel(PydanticBase):
    model_config = ConfigDict(
        alias_generator=alias_generators.to_camel,
        populate_by_name=True,
        from_attributes=True,
    )
