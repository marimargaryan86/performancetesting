import datetime
from typing import Optional

import pydantic

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
    ticket_reference: Optional[str]
    visa_number: Optional[str]
    visa_expiry: Optional[str]


class PassengerBase(base.CamelCaseBaseModel):
    age_range: AgeRange
    is_wheelchair_user: bool
    is_lead_passenger: bool
    first_name: Optional[str] = None
    sur_name: Optional[str] = None
    email: Optional[str] = None
    telephone: Optional[str] = None
    nationality: Optional[str] = None
    passport_number: Optional[str] = None
    passport_place_of_issue: Optional[str] = None
    date_of_birth: Optional[datetime.date] = None

    _normalize_date_of_birth = pydantic.validator(
        "date_of_birth",
        pre=True,
        allow_reuse=True,
    )(normalizers.datetime_str_to_date)

    class Config(object):
        json_encoders = {
            datetime.date: lambda date_object: "{0}T00:00:00".format(
                date_object.isoformat(),
            ),
        }


class Passenger(PassengerBase):
    identifier: int = pydantic.Field(..., alias="id")
    title: Optional[str]
    passenger_type: enums.PassengerType = pydantic.Field(..., alias="type")
    sequence_no: int
    place_of_birth: Optional[str]
    passport_start_date: Optional[str]
    passport_expiry_date: Optional[str]
    city_code: Optional[str]
    extra_info: Optional[ExtraInfo]


class RoutePassengerInfoExtended(base.CamelCaseBaseModel):
    route_id: int
    passenger_info: RoutePassengerInfo
