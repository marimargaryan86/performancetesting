import functools
from typing import Any, Protocol

import email_validator
import phonenumbers
import pycountry
from furl import furl


class _CountryFormatter(object):
    def validate(self, potential_country: Any) -> bool:
        return self.unmarshal(potential_country) is not None

    def unmarshal(self, country: Any) -> pycountry.db.Data | None:
        return pycountry.countries.get(alpha_2=country)


class _EmailFormatter(object):
    def validate(self, potential_email: Any) -> bool:
        try:
            self.unmarshal(potential_email)
        except email_validator.EmailNotValidError:
            return False

        return True

    def unmarshal(self, email: Any) -> str:
        return email_validator.validate_email(
            email=email,
            check_deliverability=False,
        ).email


class _PhoneFormatter(object):
    def validate(self, potential_phone: Any) -> bool:
        try:
            phone = self.unmarshal(potential_phone)
        except phonenumbers.NumberParseException:
            return False

        return phonenumbers.is_valid_number(phone)

    def unmarshal(self, phone: Any) -> phonenumbers.PhoneNumber:
        return phonenumbers.parse(phone, None)


class _UriFormatter(object):
    def validate(self, potential_url: Any) -> bool:
        try:
            url = self.unmarshal(potential_url)
        except ValueError:
            return False

        return bool(url.scheme)

    def unmarshal(self, url: Any) -> furl:
        return furl(url)


class _Formatter(Protocol):
    def validate(self, input_: Any) -> bool:
        """Check if the input validates against the format."""

    def unmarshal(self, input_: Any) -> Any:
        """Unmarshal the input."""


@functools.cache
def custom_formatters() -> dict[str, _Formatter]:
    return {
        "country": _CountryFormatter(),
        "email": _EmailFormatter(),
        "phone": _PhoneFormatter(),
        "uri": _UriFormatter(),
    }
