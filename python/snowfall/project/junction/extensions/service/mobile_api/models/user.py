import datetime
from collections.abc import Mapping, Sequence
from typing import Any, Self

import pydantic

from snowfall.stdlib import string


class UserGroup(pydantic.BaseModel):
    name: str | None


class User(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(
        alias_generator=string.to_lower_camel,
        populate_by_name=True,
    )

    first_name: str | None = None
    last_name: str | None = None
    phone: Mapping[str, str] | None = None
    gender: str | None = None
    country_code: str | None = None
    date_of_birth: Mapping[str, int] | None = None
    title: str | None = None
    loyalty_programs: Sequence[Mapping[str, str]] | None = None

    @classmethod
    def from_dict(cls, input_dict: Mapping[str, Any]) -> Self:
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
    email: str | None = None
