import dataclasses
from typing import Any, Dict, Mapping, Optional, Sequence

from snowfall.vendor.junction import models
from snowfall.vendor.junction.client import (  # noqa: WPS450,WPS235
    _ATTRIBUTES_KEY,
    _DATA_KEY,
    _ID_KEY,
    _METHOD_DELETE,
    _METHOD_GET,
    _METHOD_PATCH,
    _METHOD_POST,
    _PASSENGERS_KEY,
    _RELATIONSHIPS_KEY,
    _TYPE_KEY,
    JunctionClient,
    _make_pagination,
    order_includes,
)


class MobileApiClient(JunctionClient):  # noqa: WPS214
    async def create_payment(self, currency: str, amount: str) -> dict[str, Any]:
        return await self._make_request(
            method=_METHOD_POST,
            url="/payments",
            payload={
                _DATA_KEY: {
                    _TYPE_KEY: "payments",
                    _ATTRIBUTES_KEY: {
                        "currency": currency,
                        "amount": amount,
                    },
                },
            },
        )

    async def update_payment(
        self,
        payment_intent_id: str,
        voucher_id: str,
    ) -> int:
        body = {
            _DATA_KEY: {
                _TYPE_KEY: "payments",
                _RELATIONSHIPS_KEY: {
                    "voucher": {
                        _DATA_KEY: {
                            _TYPE_KEY: "vouchers",
                            _ID_KEY: voucher_id,
                        },
                    },
                },
            },
        }
        response = await self._client.request(
            method=_METHOD_PATCH,
            url="/payments/{0}".format(payment_intent_id),
            json=body,
        )
        response.raise_for_status()
        return response.status_code

    async def create_order(
        self,
        quote_id: str,
        passengers: Sequence[models.Passenger],
        contact_details: models.ContactDetails,
        include: Optional[Sequence[order_includes]] = None,
    ) -> dict[str, Any]:
        raise RuntimeError(
            "This client cannot create orders without payments. "
            + "Please, use create_order_with_payments",
        )

    async def create_order_with_payment(  # noqa: WPS211
        self,
        offer_id: str,
        option_ids: Sequence[str],
        passengers: Sequence[models.Passenger],
        contact_details: models.ContactDetails,
        payment_id: str,
        voucher_id: Optional[str] = None,
        include: Optional[Sequence[order_includes]] = None,
    ) -> dict[str, Any]:
        body: Dict[str, Dict[str, Any]]
        body = {
            _DATA_KEY: {
                _ATTRIBUTES_KEY: {
                    _PASSENGERS_KEY: [
                        dataclasses.asdict(
                            passenger,
                            dict_factory=models.dict_factory_to_camel,
                        )
                        for passenger in passengers
                    ],
                    "contactDetails": dataclasses.asdict(
                        contact_details,
                        dict_factory=models.dict_factory_to_camel,
                    ),
                },
                _RELATIONSHIPS_KEY: {
                    "offer": {
                        _DATA_KEY: {
                            _ID_KEY: offer_id,
                            _TYPE_KEY: "offers",
                        },
                    },
                    "options": {
                        _DATA_KEY: [
                            {
                                _ID_KEY: option_id,
                                _TYPE_KEY: "offer-options",
                            }
                            for option_id in option_ids
                        ],
                    },
                    "payment": {
                        _DATA_KEY: {_TYPE_KEY: "payments", _ID_KEY: payment_id},
                    },
                },
                _TYPE_KEY: "orders",
            },
        }
        if voucher_id:
            body[_DATA_KEY][_RELATIONSHIPS_KEY]["voucher"] = {
                _DATA_KEY: {
                    _TYPE_KEY: "vouchers",
                    _ID_KEY: voucher_id,
                },
            }
        query_parameters: dict[str, str] = {}
        if include:
            query_parameters["include"] = ",".join(include)
        return await self._make_request(
            method=_METHOD_POST,
            url="/orders",
            payload=body,
            query_parameters=query_parameters,
        )

    async def add_forward_order(
        self,
        order_id: str,
        email: str,
    ) -> dict[str, Any]:
        body = {
            _DATA_KEY: {
                _ATTRIBUTES_KEY: {
                    "email": email,
                },
                _TYPE_KEY: "email-messages",
            },
        }
        return await self._make_request(
            method=_METHOD_POST,
            url="/orders/{0}/messages".format(order_id),
            payload=body,
        )

    async def create_users_groups(
        self,
        group_name: str,
    ) -> dict[str, Any]:
        body = {
            _DATA_KEY: {
                _TYPE_KEY: "user-groups",
                _ATTRIBUTES_KEY: {
                    "name": group_name,
                },
            },
        }
        return await self._make_request(
            method=_METHOD_POST,
            url="/users/groups",
            payload=body,
        )

    async def add_user_group_member(  # noqa: WPS234, WPS211
        self,
        group_id: str,
        email: Optional[str] = None,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        phone: Optional[str] = None,
        gender: Optional[str] = None,
        title: Optional[str] = None,
        country_code: Optional[str] = None,
        date_of_birth: Optional[str] = None,
        loyalty_programs: Optional[Sequence[Mapping[str, Any]]] = None,
        old_password: Optional[str] = None,
        new_password: Optional[str] = None,
    ) -> dict[str, Any]:
        attributes = {
            "firstName": first_name,
            "lastName": last_name,
            "email": email,
            "phone": phone,
            "gender": gender,
            "title": title,
            "countryCode": country_code,
            "dateOfBirth": date_of_birth,
            "loyaltyPrograms": loyalty_programs,
            "oldPassword": old_password,
            "newPassword": new_password,
        }

        body = {
            _DATA_KEY: {
                _TYPE_KEY: "user-group-members",
                _ATTRIBUTES_KEY: attributes,
            },
        }
        return await self._make_request(
            method=_METHOD_POST,
            url="/users/groups/{0}/members".format(group_id),
            payload=body,
        )

    async def update_user_group_member(  # noqa: WPS234, WPS211
        self,
        member_id: str,
        email: Optional[str] = None,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        phone: Optional[str] = None,
        gender: Optional[str] = None,
        title: Optional[str] = None,
        country_code: Optional[str] = None,
        date_of_birth: Optional[str] = None,
        loyalty_programs: Optional[Sequence[Mapping[str, Any]]] = None,
        old_password: Optional[str] = None,
        new_password: Optional[str] = None,
    ) -> dict[str, Any]:
        attributes = {
            "firstName": first_name,
            "lastName": last_name,
            "email": email,
            "phone": phone,
            "gender": gender,
            "title": title,
            "countryCode": country_code,
            "dateOfBirth": date_of_birth,
            "loyaltyPrograms": loyalty_programs,
            "oldPassword": old_password,
            "newPassword": new_password,
        }

        body = {
            _DATA_KEY: {
                _TYPE_KEY: "user-group-members",
                _ATTRIBUTES_KEY: attributes,
            },
        }
        return await self._make_request(
            method=_METHOD_PATCH,
            url="/users/groups/members/{0}".format(member_id),
            payload=body,
        )

    async def update_trip_group(
        self,
        group_id: str,
        group_name: str,
    ) -> dict[str, Any]:
        attributes = {
            "name": group_name,
        }
        body = {
            _DATA_KEY: {
                _TYPE_KEY: "user-groups",
                _ATTRIBUTES_KEY: attributes,
            },
        }
        return await self._make_request(
            method=_METHOD_PATCH,
            url="/users/groups/{0}".format(group_id),
            payload=body,
        )

    async def list_user_groups(
        self,
        limit: Optional[int] = None,
        cursor: Optional[str] = None,
    ) -> dict[str, Any]:
        return await self._make_request(
            method=_METHOD_GET,
            url="/users/groups",
            query_parameters=_make_pagination(limit, cursor),
        )

    async def get_user_group(
        self,
        group_id: str,
    ) -> dict[str, Any]:
        return await self._make_request(
            method=_METHOD_GET,
            url="/users/groups/{0}".format(group_id),
        )

    async def list_user_group_members(
        self,
        group_id: str,
    ) -> dict[str, Any]:
        return await self._make_request(
            method=_METHOD_GET,
            url="/users/groups/{group_id}/members".format(group_id=group_id),
        )

    async def delete_user_group(
        self,
        group_id: str,
    ) -> dict[str, Any]:
        return await self._make_request(
            method=_METHOD_DELETE,
            url="/users/groups/{0}".format(group_id),
        )

    async def delete_user_group_member(
        self,
        member_id: str,
    ) -> dict[str, Any]:
        return await self._make_request(
            method=_METHOD_DELETE,
            url="/users/groups/members/{0}".format(member_id),
        )
