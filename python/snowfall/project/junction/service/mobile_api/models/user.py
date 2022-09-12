import datetime
from typing import Any, Mapping, Optional, Sequence

import pydantic

from snowfall.stdlib import string


class User(pydantic.BaseModel):
    first_name: Optional[str]
    last_name: Optional[str]
    phone: Optional[Mapping[str, str]]
    gender: Optional[str]
    country_code: Optional[str]
    date_of_birth: Optional[Mapping[str, int]]
    title: Optional[str]
    loyalty_programs: Optional[Sequence[Mapping[str, str]]]  # noqa: WPS234

    class Config(object):
        alias_generator = string.to_camel
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
