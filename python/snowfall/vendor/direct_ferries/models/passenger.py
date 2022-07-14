import datetime
from typing import Optional

import pydantic

from snowfall.vendor.ask2go.models import base
from snowfall.vendor.direct_ferries import enums, normalizers
from snowfall.vendor.direct_ferries.models import common


class RoutePassengerInfo(base.CamelCaseBaseModel):
    need_nationality: bool
    need_place_of_birth: bool
    need_date_of_birth: bool
    need_passport: bool
    need_passport_start_date: bool
    need_passport_expiry_date: bool


class ExtraInfo(base.CamelCaseBaseModel):
    ticket_reference: Optional[str]
    visa_number: Optional[str]
    visa_expiry: Optional[str]


class PassengerBase(base.CamelCaseBaseModel):
    age_range: common.AgeRange
    is_wheelchair_user: bool
    is_lead_passenger: bool
    first_name: str
    sur_name: str
    email: str
    telephone: str
    nationality: str
    passport_number: str
    date_of_birth: datetime.date

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
