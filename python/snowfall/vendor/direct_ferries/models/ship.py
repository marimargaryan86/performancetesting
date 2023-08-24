from collections.abc import Sequence

from pydantic import v1 as pydantic

from snowfall.vendor.direct_ferries.models import base


class OnboardFacility(base.CamelCaseBaseModel):
    identifier: int = pydantic.Field(..., alias="id")
    name: str


class Ship(base.CamelCaseBaseModel):
    name: str | None
    onboard_facilities: Sequence[OnboardFacility] | None
