from typing import Optional, Sequence

import pydantic

from snowfall.vendor.direct_ferries.models import base


class OnboardFacility(base.CamelCaseBaseModel):
    identifier: int = pydantic.Field(..., alias="id")
    name: str


class Ship(base.CamelCaseBaseModel):
    name: Optional[str]
    onboard_facilities: Optional[Sequence[OnboardFacility]]
