import datetime
from collections.abc import Mapping, Sequence
from typing import Any

import pydantic

from snowfall.stdlib import string


class User(pydantic.BaseModel):
    first_name: str | None
    last_name: str | None
    phone: Mapping[str, str] | None
    gender: str | None
    country_code: str | None
    date_of_birth: Mapping[str, int] | None
    title: str | None
    loyalty_programs: Sequence[Mapping[str, str]] | None

    class Config(object):
        alias_generator = string.to_lower_camel
        allow_population_by_field_name = True

    @classmethod
    def from_dict(cls, input_dict: Mapping[str, Any]) -> "User":
        out_dict: dict[str, Any] = {}
        for key, attribute in input_dict.items():
            if key == "phone":
                out_dict[key] = {"e164_number": attribute}
            elif key == "dateOfBirth":
                dob = datetime.date.fromisoformat(attribute)
                out_dict[key] = {
                    "year": dob.year,
                    "month": dob.month,
                    "day": dob.day,
                }
            else:
                out_dict[key] = attribute
        return cls(**out_dict)


class UserGroupMember(User):
    email: str | None
