from typing import Optional

import pydantic

from snowfall.vendor.direct_ferries.models import base


class Operator(base.CamelCaseBaseModel):
    identifier: int = pydantic.Field(..., alias="id")
    name: str
    connection_type: Optional[str]


class OperatorDetails(base.CamelCaseBaseModel):
    identifier: int = pydantic.Field(..., alias="id")
    name: str
