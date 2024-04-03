import datetime
from types import MappingProxyType

from pydantic import v1 as pydantic

from snowfall.vendor.direct_ferries import enums, normalizers
from snowfall.vendor.direct_ferries.models import base


class AgeRange(pydantic.BaseModel):
    age_from: int = pydantic.Field(..., alias="from")
    age_to: int = pydantic.Field(..., alias="to")


class RoutePassengerInfo(base.CamelCaseBaseModel):
    need_nationality: bool
    need_place_of_birth: bool
    need_date_of_birth: bool = pydantic.Field(..., alias="needDateOfBith")
    need_passport: bool
    need_passport_start_date: bool
    need_passport_expiry_date: bool


class ExtraInfo(base.CamelCaseBaseModel):
    ticket_reference: str | None
    visa_number: str | None
    visa_expiry: str | None


class PassengerBase(base.CamelCaseBaseModel):
    age_range: AgeRange
    is_wheelchair_user: bool
    is_lead_passenger: bool
    first_name: str | None = None
    sur_name: str | None = None
    email: str | None = None
    telephone: str | None = None
    nationality: str | None = None
    passport_number: str | None = None
    passport_place_of_issue: str | None = None
    date_of_birth: datetime.date | None = None

    _normalize_date_of_birth = pydantic.validator(
        "date_of_birth",
        pre=True,
        allow_reuse=True,
    )(normalizers.datetime_str_to_date)

    class Config:
        json_encoders = MappingProxyType(
            {
                datetime.date: lambda date_object: "{0}T00:00:00".format(
                    date_object.isoformat(),
                ),
            },
        )


class Passenger(PassengerBase):
    identifier: int = pydantic.Field(..., alias="id")
    title: str | None
    passenger_type: enums.PassengerType = pydantic.Field(..., alias="type")
    sequence_no: int
    place_of_birth: str | None
    passport_start_date: str | None
    passport_expiry_date: str | None
    city_code: str | None
    extra_info: ExtraInfo | None


class RoutePassengerInfoExtended(base.CamelCaseBaseModel):
    route_id: int
    passenger_info: RoutePassengerInfo
