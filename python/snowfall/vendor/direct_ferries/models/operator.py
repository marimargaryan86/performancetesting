from collections.abc import Sequence

import pydantic

from snowfall.vendor.direct_ferries.models import base


class Operator(base.CamelCaseBaseModel):
    identifier: int = pydantic.Field(..., alias="id")
    name: str
    connection_type: str | None


class OperatorDetails(base.CamelCaseBaseModel):
    identifier: int = pydantic.Field(..., alias="id")
    name: str


class OperatorData(base.CamelCaseBaseModel):
    operators: Sequence[Operator]


class OperatorResponse(base.CamelCaseBaseModel):
    operator_data: OperatorData = pydantic.Field(..., alias="data")
