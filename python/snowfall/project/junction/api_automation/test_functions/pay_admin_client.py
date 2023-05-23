from __future__ import annotations

import json
import logging
import sys
from typing import Any, Awaitable, Callable, Literal, Sequence
from urllib.parse import parse_qs, urlparse

import httpx

from snowfall.vendor.junction.client import BaseClient, make_pagination_params

_DATA_KEY = "data"
_ID_KEY = "id"
_TYPE_KEY = "type"
_RELATIONSHIPS_KEY = "relationships"
_ATTRIBUTES_KEY = "attributes"
_LIMIT_KEY = "page[limit]"
_CURSOR_KEY = "page[cursor]"
conversion_includes = Literal["transactions"]

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


class PayAdminClient(BaseClient):  # noqa: WPS214
    async def create_company(  # noqa: WPS211
        self,
        company: str,
        address_lines: Sequence[str],
        country_code: str,
        postal_code: str,
        city: str,
        fx_markup: float,
        processing_markup: float,
        sales_markup: float,
    ) -> dict[str, Any]:
        payload = {
            _DATA_KEY: {
                _TYPE_KEY: "companies",
                _ATTRIBUTES_KEY: {
                    "name": company,
                    "address": {
                        "addressLines": address_lines,
                        "countryCode": country_code,
                        "postalCode": postal_code,
                        "city": city,
                    },
                    "fxMarkup": fx_markup,
                    "processingMarkup": processing_markup,
                    "salesMarkup": sales_markup,
                },
            },
        }
        logger.info("payload %s", json.dumps(payload, indent=4))

        response = await self.client.post(
            "/companies",
            json=payload,
        )

        response.raise_for_status()
        return response.json()

    async def get_account(
        self,
        account_id: str,
    ) -> dict[str, Any]:
        response = await self.client.get(
            "/accounts/{0}".format(account_id),
        )

        response.raise_for_status()
        return response.json()

    async def get_accounts(
        self,
        limit: int | None = None,
        cursor: str | None = None,
        sort: str | None = None,
    ) -> dict[str, Any]:
        response = await self.client.get(
            "accounts",
            params=make_pagination_params(limit, cursor, sort),
        )
        response.raise_for_status()
        return response.json()

    async def get_balances(
        self,
        account_id: str,
        limit: int | None = None,
        cursor: str | None = None,
    ) -> dict[str, Any]:
        response = await self.client.get(
            "/accounts/{0}/balances".format(account_id),
            params=make_pagination_params(limit, cursor),
        )

        response.raise_for_status()
        return response.json()

    async def get_company_details(
        self,
        company_id: str,
    ) -> dict[str, Any]:
        response = await self.client.get(
            "/companies/{0}".format(company_id),
        )

        response.raise_for_status()
        return response.json()

    async def get_conversion_details(
        self,
        conversion_id: str,
        include: Sequence[conversion_includes] | None = None,
    ) -> dict[str, Any]:
        response = await self.client.get(
            "/conversions/{0}".format(conversion_id),
            params=make_pagination_params(limit=None, cursor=None, include=include),
        )

        response.raise_for_status()
        return response.json()

    async def get_transactions(
        self,
    ) -> dict[str, Any]:
        response = await self.client.get(
            "/transactions",
        )

        response.raise_for_status()
        return response.json()

    async def update_company(  # noqa: WPS211
        self,
        company_id: str,
        company: str,
        address_lines: Sequence[str],
        country_code: str,
        postal_code: str,
        city: str,
        fx_markup: float,
        processing_markup: float,
        sales_markup: float,
    ) -> dict[str, Any]:
        payload = {
            _DATA_KEY: {
                _TYPE_KEY: "companies",
                _ATTRIBUTES_KEY: {
                    "name": company,
                    "address": {
                        "addressLines": address_lines,
                        "countryCode": country_code,
                        "postalCode": postal_code,
                        "city": city,
                    },
                    "fxMarkup": fx_markup,
                    "processingMarkup": processing_markup,
                    "salesMarkup": sales_markup,
                },
            },
        }
        logger.info("payload %s", json.dumps(payload, indent=4))

        response = await self.client.patch(
            "/companies/{0}".format(company_id),
            json=payload,
        )

        response.raise_for_status()
        return response.json()

    async def list_companies(
        self,
        limit: int,
        cursor: str,
    ) -> dict[str, Any]:
        response = await self.client.get(
            "/companies",
            params=make_pagination_params(limit, cursor),
        )

        response.raise_for_status()
        return response.json()

    async def list_accountless_companies(
        self,
        limit: int,
        cursor: str,
    ) -> dict[str, Any]:
        response = await self.client.get(
            "/companies/accountless",
            params=make_pagination_params(limit, cursor),
        )

        response.raise_for_status()
        return response.json()

    async def add_currency(
        self,
        account_id: str,
        currency_id: str,
    ) -> dict[str, Any]:
        payload = {
            _DATA_KEY: {
                _TYPE_KEY: "balances",
                _RELATIONSHIPS_KEY: {
                    "currency": {
                        _DATA_KEY: {
                            "id": currency_id,
                            _TYPE_KEY: "currencies",
                        },
                    },
                },
            },
        }
        logger.info("payload %s", json.dumps(payload, indent=4))

        response = await self.client.post(
            "/accounts/{0}/relationships/currencies".format(
                account_id,
            ),
            json=payload,
        )

        response.raise_for_status()
        return response.json()

    async def list_beneficiaries(
        self,
        limit: int | None = None,
        cursor: str | None = None,
    ) -> dict[str, Any]:
        response = await self.client.get(
            "/beneficiaries",
            params=make_pagination_params(limit, cursor),
        )
        response.raise_for_status()
        return response.json()

    async def get_beneficiary(
        self,
        beneficiary_id: str,
    ) -> dict[str, Any]:
        response = await self.client.get(
            "/beneficiaries/{0}".format(beneficiary_id),
        )
        response.raise_for_status()
        return response.json()

    async def create_contact(  # noqa: WPS211
        self,
        first_name: str,
        last_name: str,
        email_address: str,
        phone_number: str,
        company_id: str,
    ) -> dict[str, Any]:
        payload = {
            _DATA_KEY: {
                _TYPE_KEY: "contacts",
                _ATTRIBUTES_KEY: {
                    "firstName": first_name,
                    "lastName": last_name,
                    "emailAddress": email_address,
                    "phoneNumber": phone_number,
                },
            },
        }
        logger.info("payload %s", json.dumps(payload, indent=4))

        response = await self.client.post(
            "/companies/{0}/contacts".format(company_id),
            json=payload,
        )

        response.raise_for_status()
        return response.json()

    async def list_contacts(
        self,
        company_id: str,
        limit: int | None = None,
        cursor: str | None = None,
    ) -> dict[str, Any]:
        response = await self.client.get(
            "/companies/{0}/contacts".format(company_id),
            params=make_pagination_params(limit, cursor),
        )

        response.raise_for_status()
        return response.json()

    async def list_conversions_details(
        self,
        include: Sequence[conversion_includes] | None = None,
        limit: int | None = None,
        cursor: str | None = None,
    ) -> dict[str, Any]:
        response = await self.client.get(
            "/conversions",
            params=make_pagination_params(limit, cursor, include=include),
        )
        response.raise_for_status()
        return response.json()

    async def create_accounts(
        self,
        name: str,
        contact_id: str,
    ) -> dict[str, Any]:
        payload = {
            _DATA_KEY: {
                _TYPE_KEY: "accounts",
                _ATTRIBUTES_KEY: {
                    "name": name,
                },
                _RELATIONSHIPS_KEY: {
                    "contact": {
                        _DATA_KEY: {
                            _ID_KEY: contact_id,
                            _TYPE_KEY: "contacts",
                        },
                    },
                },
            },
        }

        response = await self.client.post(
            "/accounts",
            json=payload,
        )

        response.raise_for_status()
        return response.json()

    async def create_user(
        self,
        email: str,
        password: str,
    ) -> dict[str, Any]:
        payload = {
            _DATA_KEY: {
                _TYPE_KEY: "users",
                _ATTRIBUTES_KEY: {
                    "email": email,
                    "password": password,
                },
            },
        }
        logger.info("payload %s", json.dumps(payload, indent=4))

        response = await self.client.post(
            "/users",
            json=payload,
        )

        response.raise_for_status()
        return response.json()

    async def create_beneficiary(  # noqa: WPS211
        self,
        bank_account_holder_name: str,
        email: str,
        beneficiary_address_lines: Sequence[str],
        beneficiary_country_code: str,
        bank_name: str,
        account_type: str,
        payment_types: str,
        bank_address_lines: Sequence[str],
        bank_country_code: str,
        currency_id: str,
        account_id: str,
        account_number: str | None = None,
        beneficiary_postal_code: str | None = None,
        beneficiary_city: str | None = None,
        beneficiary_state: str | None = None,
        bic_swift: str | None = None,
        aba: str | None = None,
        iban: str | None = None,
    ) -> dict[str, Any]:
        payload = {
            _DATA_KEY: {
                _TYPE_KEY: "beneficiaries",
                _ATTRIBUTES_KEY: {
                    "bankAccountHolderName": bank_account_holder_name,
                    "email": email,
                    "beneficiaryAddress": {
                        "addressLines": beneficiary_address_lines,
                        "countryCode": beneficiary_country_code,
                        "postalCode": beneficiary_postal_code,
                        "city": beneficiary_city,
                        "state": beneficiary_state,
                    },
                    "bankDetails": {
                        "name": bank_name,
                        **(
                            {
                                "accountNumber": account_number,
                                "aba": aba,
                            }
                            if account_number
                            else {
                                "iban": iban,
                            }
                        ),
                        "bicSwift": bic_swift,
                        "accountType": account_type,
                        "paymentTypes": payment_types,
                        "address": {
                            "addressLines": bank_address_lines,
                            "countryCode": bank_country_code,
                        },
                    },
                },
                _RELATIONSHIPS_KEY: {
                    "currency": {
                        _DATA_KEY: {
                            "id": currency_id,
                            "type": "currencies",
                        },
                    },
                    "account": {
                        _DATA_KEY: {
                            "id": account_id,
                            "type": "accounts",
                        },
                    },
                },
            },
        }
        logger.info("payload %s", json.dumps(payload, indent=4))
        response = await self.client.post(
            "/beneficiaries",
            json=payload,
        )

        response.raise_for_status()
        return response.json()

    async def update_beneficiary(  # noqa: WPS211
        self,
        beneficiary_id: str,
        bank_account_holder_name: str,
        email: str,
        beneficiary_address_lines: Sequence[str],
        beneficiary_country_code: str,
        bank_name: str,
        account_type: str,
        payment_types: str,
        bank_address_lines: Sequence[str],
        bank_country_code: str,
        currency_id: str,
        account_id: str,
        account_number: str | None = None,
        beneficiary_postal_code: str | None = None,
        beneficiary_city: str | None = None,
        beneficiary_state: str | None = None,
        bic_swift: str | None = None,
        aba: str | None = None,
        iban: str | None = None,
    ) -> dict[str, Any]:
        payload = {
            _DATA_KEY: {
                _TYPE_KEY: "beneficiaries",
                _ATTRIBUTES_KEY: {
                    "bankAccountHolderName": bank_account_holder_name,
                    "email": email,
                    "beneficiaryAddress": {
                        "addressLines": beneficiary_address_lines,
                        "countryCode": beneficiary_country_code,
                        "postalCode": beneficiary_postal_code,
                        "city": beneficiary_city,
                        "state": beneficiary_state,
                    },
                    "bankDetails": {
                        "name": bank_name,
                        **(
                            {
                                "accountNumber": account_number,
                                "aba": aba,
                            }
                            if account_number
                            else {
                                "iban": iban,
                            }
                        ),
                        "bicSwift": bic_swift,
                        "accountType": account_type,
                        "paymentTypes": payment_types,
                        "address": {
                            "addressLines": bank_address_lines,
                            "countryCode": bank_country_code,
                        },
                    },
                },
                _RELATIONSHIPS_KEY: {
                    "currency": {
                        _DATA_KEY: {
                            "id": currency_id,
                            "type": "currencies",
                        },
                    },
                    "account": {
                        _DATA_KEY: {
                            "id": account_id,
                            "type": "accounts",
                        },
                    },
                },
            },
        }
        logger.info("payload %s", json.dumps(payload, indent=4))
        response = await self.client.patch(
            "/beneficiaries/{0}".format(beneficiary_id),
            json=payload,
        )

        response.raise_for_status()
        return response.json()


async def get_all_resources(  # noqa: WPS210
    client_method: Callable[[int, str], Awaitable[Any]],
    limit: int,
    cursor: str,
    logger_resources: logging.Logger,
) -> list[dict[str, Any]]:
    resources: list[dict[str, Any]] = []
    while True:
        try:
            body = await client_method(limit, cursor)
        except httpx.HTTPStatusError as err:
            logger_resources.info("response headers: %s", err.response.headers)
            logger_resources.info("response body: %s", err.response.json())
            sys.exit("{0} method - is failed".format(client_method.__name__))

        if not body[_DATA_KEY]:
            break

        resources.extend(body[_DATA_KEY])
        url = body["links"]["next"]
        parse_url = urlparse(url)
        parse_data = parse_qs(parse_url.query)
        limit = int(parse_data[_LIMIT_KEY][0])
        cursor = parse_data[_CURSOR_KEY][0]

    return resources
