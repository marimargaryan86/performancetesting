from collections.abc import Sequence
from enum import Enum

from pydantic import Field

from snowfall.vendor.fluxir.models import base_models


class GetServiceIntentsRequest(base_models.CamelCaseBaseModel):
    to: str
    from_: str = Field(..., alias="from")
    nationality_country_code: str
    destination_country_code: str
    trip_purpose: str


class PeriodUnit(Enum):
    days = "Days"
    weeks = "Weeks"
    months = "Months"
    years = "Years"


class ServiceIntent(base_models.CamelCaseBaseModel):
    redirect_uri: str
    title: str | None
    description: str | None
    info: str | None
    fee: int
    approval_rate: str
    appliers_count: str
    expected_processing_time: str
    stay_duration: str
    stay_duration_unit: PeriodUnit
    validity_period: str | None
    validity_period_unit: PeriodUnit


class GetServiceIntentsResponse(base_models.CamelCaseBaseModel):
    items: Sequence[ServiceIntent]
