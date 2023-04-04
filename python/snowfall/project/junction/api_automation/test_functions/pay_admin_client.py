from __future__ import annotations

import logging
import sys
from typing import Any, Sequence
from urllib.parse import parse_qs, urlencode, urlparse

import httpx

from snowfall.vendor.junction.client import BaseClient

_DATA_KEY = "data"
_ID_KEY = "id"
_TYPE_KEY = "type"
_RELATIONSHIPS_KEY = "relationships"
_ATTRIBUTES_KEY = "attributes"
_LIMIT_KEY = "page[limit]"
_CURSOR_KEY = "page[cursor]"


class PayAdminClient(BaseClient):  # noqa: WPS214
    async def create_company(  # noqa: WPS211
        self,
        company: str,
        address_lines: Sequence[str],
        country_code: str,
        postal_code: str,
        city: str,
        fx_markup: float,
        fx_provider_markup: float,
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
                    "fxProviderMarkup": fx_provider_markup,
                    "salesMarkup": sales_markup,
                },
            },
        }

        response = await self._client.post(
            "{0}/companies".format(self._base_url),
            json=payload,
        )

        response.raise_for_status()
        return response.json()

    async def get_accounts(
        self,
        limit: int | None = None,
        cursor: str | None = None,
        sort: str | None = None,
    ) -> dict[str, Any]:
        response = await self._client.get(
            "{0}/accounts".format(self._base_url),
            params=_make_pagination_with_sorting(cursor, limit, sort),
        )
        response.raise_for_status()
        return response.json()

    async def get_balances(
        self,
        account_id: str,
        limit: int | None = None,
        cursor: str | None = None,
    ) -> dict[str, Any]:
        response = await self._client.get(
            "{0}/accounts/{1}/balances".format(self._base_url, account_id),
            params=_make_pagination(limit, cursor),
        )

        response.raise_for_status()
        return response.json()

    async def get_company_details(
        self,
        company_id: str,
    ) -> dict[str, Any]:
        response = await self._client.get(
            "{0}/companies/{1}".format(self._base_url, company_id),
        )

        response.raise_for_status()
        return response.json()

    async def get_conversion_details(
        self,
        conversion_id: str,
    ) -> dict[str, Any]:
        response = await self._client.get(
            "{0}/conversions/{1}".format(self._base_url, conversion_id),
        )

        response.raise_for_status()
        return response.json()

    async def get_transactions(
        self,
    ) -> dict[str, Any]:
        response = await self._client.get(
            "{0}/transactions".format(self._base_url),
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
        fx_provider_markup: float,
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
                    "fxProviderMarkup": fx_provider_markup,
                    "salesMarkup": sales_markup,
                },
            },
        }

        response = await self._client.patch(
            "{0}/companies/{1}".format(self._base_url, company_id),
            json=payload,
        )

        response.raise_for_status()
        return response.json()

    async def list_companies(
        self,
        limit: int,
        cursor: str,
    ) -> dict[str, Any]:
        query_params = urlencode(_make_pagination(limit, cursor))
        response = await self._client.get(
            "/companies?{0}".format(query_params) if query_params else "/companies",
        )

        response.raise_for_status()
        return response.json()

    async def list_accountless_companies(
        self,
        limit: int,
        cursor: str,
    ) -> dict[str, Any]:
        query_params = urlencode(_make_pagination(limit, cursor))
        response = await self._client.get(
            (
                "/companies/accountless?{0}".format(query_params)
                if query_params
                else "/companies/accountless"
            ),
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

        response = await self._client.post(
            "{0}/accounts/{1}/relationships/currencies".format(
                self._base_url,
                account_id,
            ),
            json=payload,
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

        response = await self._client.post(
            "{0}/companies/{1}/contacts".format(self._base_url, company_id),
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
        response = await self._client.get(
            "/companies/{0}/contacts".format(company_id),
            params=_make_pagination(limit, cursor),
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

        response = await self._client.post(
            "{0}/accounts".format(self._base_url),
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
        response = await self._client.post(
            "/users",
            json=payload,
        )

        response.raise_for_status()
        return response.json()


async def get_all_resources(  # noqa: WPS210
    client_method: Any,
    limit: int,
    cursor: str,
    logger: logging.Logger,
) -> list[dict[str, Any]]:
    resources: list[dict[str, Any]] = []
    while True:
        try:
            body = await client_method(limit, cursor)
        except httpx.HTTPStatusError as err:
            logger.info("response headers: %s", err.response.headers)
            logger.info("response body: %s", err.response.json())
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


def _make_pagination_with_sorting(
    cursor: str | None = None,
    limit: int | None = None,
    sort: str | None = None,
) -> dict[str, Any]:
    return (
        {"sort": sort, **_make_pagination(limit, cursor)}
        if sort
        else _make_pagination(limit, cursor)
    )


def _make_pagination(
    limit: int | None,
    cursor: str | None,
) -> dict[str, int | str]:
    return {
        key: pagination_value
        for key, pagination_value in ((_LIMIT_KEY, limit), (_CURSOR_KEY, cursor))
        if pagination_value
    }
