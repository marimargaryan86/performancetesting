import dataclasses
from typing import Any, Sequence

from snowfall.stdlib import string


def dict_factory_to_camel(dict_items: Sequence[tuple[str, Any]]) -> dict[str, Any]:
    return {
        string.to_camel(dict_key): dict_value for dict_key, dict_value in dict_items
    }


@dataclasses.dataclass(frozen=True)
class Passenger(object):
    first_name: str
    last_name: str
    title: str
    gender: str
    date_of_birth: str


@dataclasses.dataclass(frozen=True)
class Address(object):
    address_lines: Sequence[str]
    country_code: str
    postal_code: str
    city: str


@dataclasses.dataclass(frozen=True)
class ContactDetails(object):
    email: str
    address: Address
    phone_number: str
