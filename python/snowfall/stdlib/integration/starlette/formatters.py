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
        return self.format(potential_country) is not None

    def format(self, country: Any) -> pycountry.db.Data | None:  # noqa: A003
        return pycountry.countries.get(alpha_2=country)


class _CurrencyFormatter(formatters.Formatter):
    def validate(self, potential_currency: Any) -> bool:
        return self.format(potential_currency) is not None

    def format(self, currency: Any) -> iso4217.Currency | None:  # noqa: A003
        try:
            return iso4217.Currency(currency)
        except ValueError:
            return None


class _EmailFormatter(formatters.Formatter):
    def validate(self, potential_email: Any) -> bool:
        try:
            self.format(potential_email)
        except email_validator.EmailNotValidError:
            return False

        return True

    def format(self, email: Any) -> str:  # noqa: A003
        return email_validator.validate_email(
            email=email,
            check_deliverability=False,
        ).email


class _PhoneFormatter(formatters.Formatter):
    def validate(self, potential_phone: Any) -> bool:
        try:
            phone = self.format(potential_phone)
        except phonenumbers.NumberParseException:
            return False

        return phonenumbers.is_valid_number(phone)

    def format(self, phone: Any) -> phonenumbers.PhoneNumber:  # noqa: A003
        return phonenumbers.parse(phone, None)


class _UriFormatter(formatters.Formatter):
    def validate(self, potential_url: Any) -> bool:
        try:
            url = self.format(potential_url)
        except ValueError:
            return False

        return bool(url.scheme)

    def format(self, url: Any) -> furl:  # noqa: A003
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
