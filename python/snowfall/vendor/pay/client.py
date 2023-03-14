from __future__ import annotations

from typing import Any, AsyncGenerator, Mapping, Sequence

import httpx

_DATA_KEY = "data"
_ID_KEY = "id"
_TYPE_KEY = "type"
_RELATIONSHIPS_KEY = "relationships"
_ATTRIBUTES_KEY = "attributes"
_PASSENGERS_KEY = "passengers"
_LIMIT_KEY = "page[limit]"
_CURSOR_KEY = "page[cursor]"
_METHOD_GET = "GET"
_METHOD_POST = "POST"
_METHOD_PATCH = "PATCH"
_METHOD_DELETE = "DELETE"
_EMAIL_KEY = "email"
_PASSWORD_KEY = "password"  # nosec


class PayTokenAuth(httpx.Auth):
    def __init__(
        self,
        token: str,
        headers: Mapping[str, Any],
    ):
        self._token = token
        self._headers = headers

    async def async_auth_flow(
        self,
        request: httpx.Request,
    ) -> AsyncGenerator[httpx.Request, httpx.Response]:
        request.headers.update(
            httpx.Headers(
                {
                    "Authorization": "Bearer {0}".format(self._token),
                },
            ),
        )
        yield request


class PayAuthentication(httpx.Auth):
    def __init__(
        self,
        base_url: str,
        headers: httpx.Headers,
        email: str,
        password: str,
    ):
        self._base_url = base_url
        self._headers = headers
        self._email = email
        self._password = password

    async def async_auth_flow(
        self,
        request: httpx.Request,
    ) -> AsyncGenerator[httpx.Request, httpx.Response]:
        response = await self.create_authentication_token()
        request.headers["Authorization"] = "Bearer {0}".format(
            response[_DATA_KEY][_ATTRIBUTES_KEY]["token"],
        )
        request.headers.update(self._headers)
        yield request

    async def create_authentication_token(
        self,
    ) -> dict[str, Any]:
        payload = {
            _DATA_KEY: {
                _TYPE_KEY: "user-tokens",
                _ATTRIBUTES_KEY: {
                    "email": self._email,
                    "password": self._password,
                },
            },
        }

        client = httpx.AsyncClient(verify=False, http2=True)
        response = await client.request(
            method=_METHOD_POST,
            url="{0}/users/tokens".format(self._base_url),
            headers=self._headers,
            json=payload,
        )
        response.raise_for_status()

        return response.json()


class PayClient(object):
    def __init__(
        self,
        base_url: str,
        auth: httpx.Auth,
        client: httpx.AsyncClient | None = None,
    ):
        self._base_url = base_url
        self._http_client = client or httpx.AsyncClient(
            base_url=base_url,
            verify=False,
            http2=True,
            auth=auth,
        )

    async def create_quote(  # noqa: WPS211
        self,
        amount: int,
        payer_id: str,
        beneficiary_id: str,
        from_currency: str,
        to_currency: str,
    ) -> dict[str, Any]:
        payload = {
            _DATA_KEY: {
                _TYPE_KEY: "quotes",
                _ATTRIBUTES_KEY: {
                    "amount": amount,
                },
                "relationships": {
                    "fromCurrency": {
                        "data": {
                            "id": from_currency,
                            _TYPE_KEY: "currencies",
                        },
                    },
                    "payer": {"data": {"id": payer_id, _TYPE_KEY: "companies"}},
                    "beneficiary": {
                        "data": {"id": beneficiary_id, _TYPE_KEY: "companies"},
                    },
                    "toCurrency": {
                        "data": {"id": to_currency, _TYPE_KEY: "currencies"},
                    },
                },
            },
        }

        response = await self._http_client.post(
            "{0}/quotes".format(self._base_url),
            headers=self._http_client.headers,
            json=payload,
        )

        response.raise_for_status()
        return response.json()

    async def create_transactions(
        self,
        external_reference: str,
        parent_external_reference: str,
        quotation_id: str,
    ) -> dict[str, Any]:
        payload = {
            _DATA_KEY: {
                _TYPE_KEY: "transactions",
                _ATTRIBUTES_KEY: {
                    "externalReference": external_reference,
                    "parentExternalReference": parent_external_reference,
                },
                "relationships": {
                    "quotation": {
                        "data": {
                            "id": quotation_id,
                            "type": "quotations",
                        },
                    },
                },
            },
        }

        response = await self._http_client.post(
            "{0}/transactions".format(self._base_url),
            headers=self._http_client.headers,
            json=payload,
        )

        response.raise_for_status()
        return response.json()


class PayAdminClient(object):  # noqa: WPS214
    def __init__(
        self,
        base_url: str,
        auth: httpx.Auth,
        client: httpx.AsyncClient | None = None,
    ):
        self._base_url = base_url
        self._http_client = client or httpx.AsyncClient(
            base_url=base_url,
            verify=False,
            http2=True,
            auth=auth,
        )

    async def create_company(  # noqa: WPS211
        self,
        company: str,
        address_lines: Sequence[str],
        country_code: str,
        postal_code: str,
        city: str,
        buffer_rate: float,
        sales_rate: float,
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
                    "bufferRate": buffer_rate,
                    "salesRate": sales_rate,
                },
            },
        }

        response = await self._http_client.post(
            "{0}/companies".format(self._base_url),
            headers=self._http_client.headers,
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
        response = await self._http_client.get(
            "{0}/accounts".format(self._base_url),
            headers=self._http_client.headers,
            params=(
                {"sort": sort, **_make_pagination(limit, cursor)}
                if sort
                else _make_pagination(limit, cursor)
            ),
        )
        response.raise_for_status()
        return response.json()

    async def get_balances(
        self,
        account_id: str,
        limit: int | None = None,
        cursor: str | None = None,
    ) -> dict[str, Any]:
        response = await self._http_client.get(
            "{0}/accounts/{1}/balances".format(self._base_url, account_id),
            headers=self._http_client.headers,
            params=_make_pagination(limit, cursor),
        )

        response.raise_for_status()
        return response.json()

    async def get_company_details(
        self,
        company_id: str,
    ) -> dict[str, Any]:
        response = await self._http_client.get(
            "{0}/companies/{1}".format(self._base_url, company_id),
            headers=self._http_client.headers,
        )

        response.raise_for_status()
        return response.json()

    async def get_conversion_details(
        self,
        conversion_id: str,
    ) -> dict[str, Any]:
        response = await self._http_client.get(
            "{0}/conversions/{1}".format(self._base_url, conversion_id),
            headers=self._http_client.headers,
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
        buffer_rate: float,
        sales_rate: float,
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
                    "bufferRate": buffer_rate,
                    "salesRate": sales_rate,
                },
            },
        }

        response = await self._http_client.patch(
            "{0}/companies/{1}".format(self._base_url, company_id),
            headers=self._http_client.headers,
            json=payload,
        )

        response.raise_for_status()
        return response.json()

    async def create_contact_persons(  # noqa: WPS211
        self,
        first_name: str,
        last_name: str,
        email_address: str,
        phone_number: str,
        company_id: str,
    ) -> dict[str, Any]:
        payload = {
            _DATA_KEY: {
                _TYPE_KEY: "contact-persons",
                _ATTRIBUTES_KEY: {
                    "firstName": first_name,
                    "lastName": last_name,
                    "emailAddress": email_address,
                    "phoneNumber": phone_number,
                },
                _RELATIONSHIPS_KEY: {
                    "company": {
                        _DATA_KEY: {_ID_KEY: company_id, _TYPE_KEY: "companies"},
                    },
                },
            },
        }

        response = await self._http_client.post(
            "{0}/contact-persons".format(self._base_url),
            headers=self._http_client.headers,
            json=payload,
        )

        response.raise_for_status()
        return response.json()

    async def create_accounts(
        self,
        name: str,
        contact_person_id: str,
    ) -> dict[str, Any]:
        payload = {
            _DATA_KEY: {
                _TYPE_KEY: "accounts",
                _ATTRIBUTES_KEY: {
                    "name": name,
                },
                _RELATIONSHIPS_KEY: {
                    "contactPerson": {
                        _DATA_KEY: {
                            _ID_KEY: contact_person_id,
                            _TYPE_KEY: "contact-persons",
                        },
                    },
                },
            },
        }

        response = await self._http_client.post(
            "{0}/accounts".format(self._base_url),
            headers=self._http_client.headers,
            json=payload,
        )

        response.raise_for_status()
        return response.json()


def _make_pagination(
    limit: int | None,
    cursor: str | None,
) -> dict[str, int | str]:
    return {
        key: pagination_value
        for key, pagination_value in ((_LIMIT_KEY, limit), (_CURSOR_KEY, cursor))
        if pagination_value
    }
