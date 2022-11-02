import functools
from typing import Any

import email_validator
import iso4217
import phonenumbers
import pycountry
from furl import furl
from openapi_core.unmarshalling.schemas import formatters


class _CountryFormatter(formatters.Formatter):
    def validate(self, potential_country: Any) -> bool:
        return self.unmarshal(potential_country) is not None

    def unmarshal(self, country: Any) -> pycountry.db.Data | None:
        return pycountry.countries.get(alpha_2=country)


class _CurrencyFormatter(formatters.Formatter):
    def validate(self, potential_currency: Any) -> bool:
        return self.unmarshal(potential_currency) is not None

    def unmarshal(self, currency: Any) -> iso4217.Currency | None:
        try:
            return iso4217.Currency(currency)
        except ValueError:
            return None


class _EmailFormatter(formatters.Formatter):
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


class _PhoneFormatter(formatters.Formatter):
    def validate(self, potential_phone: Any) -> bool:
        try:
            phone = self.unmarshal(potential_phone)
        except phonenumbers.NumberParseException:
            return False

        return phonenumbers.is_valid_number(phone)

    def unmarshal(self, phone: Any) -> phonenumbers.PhoneNumber:
        return phonenumbers.parse(phone, None)


class _UriFormatter(formatters.Formatter):
    def validate(self, potential_url: Any) -> bool:
        try:
            url = self.unmarshal(potential_url)
        except ValueError:
            return False

        return bool(url.scheme)

    def unmarshal(self, url: Any) -> furl:
        return furl(url)


@functools.cache
def custom_formatters() -> dict[str, formatters.Formatter]:
    return {
        "country": _CountryFormatter(),
        "currency": _CurrencyFormatter(),
        "email": _EmailFormatter(),
        "phone": _PhoneFormatter(),
        "uri": _UriFormatter(),
    }
