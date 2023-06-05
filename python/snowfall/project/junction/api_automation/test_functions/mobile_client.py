import dataclasses
from datetime import date, datetime
from typing import Any, Dict, Mapping, Sequence

from snowfall.vendor.junction.go import models
from snowfall.vendor.junction.go.client import (  # noqa: WPS450,WPS235
    _ATTRIBUTES_KEY,
    _DATA_KEY,
    _EMAIL_KEY,
    _ID_KEY,
    _METHOD_DELETE,
    _METHOD_GET,
    _METHOD_PATCH,
    _METHOD_POST,
    _PASSENGERS_KEY,
    _PASSWORD_KEY,
    _RELATIONSHIPS_KEY,
    _TYPE_KEY,
    Client,
    LegType,
    _make_pagination,
    order_includes,
)


class MobileApiClient(Client):  # noqa: WPS214
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
        response = await self.client.request(
            method=_METHOD_PATCH,
            url="/payments/{0}".format(payment_intent_id),
            json=body,
        )
        response.raise_for_status()
        return response.status_code

    async def create_order(  # noqa: WPS211
        self,
        quote_id: str,
        passengers: Sequence[models.Passenger],
        contact_details: models.ContactDetails,
        residence_address: models.Address | None = None,
        include: Sequence[order_includes] | None = None,
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
        voucher_id: str | None = None,
        include: Sequence[order_includes] | None = None,
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

    async def add_user_group_member(  # noqa: WPS211
        self,
        group_id: str,
        email: str | None = None,
        first_name: str | None = None,
        last_name: str | None = None,
        phone: str | None = None,
        gender: str | None = None,
        title: str | None = None,
        country_code: str | None = None,
        date_of_birth: str | None = None,
        loyalty_programs: Sequence[Mapping[str, Any]] | None = None,
        old_password: str | None = None,
        new_password: str | None = None,
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

    async def update_user_group_member(  # noqa: WPS211
        self,
        member_id: str,
        email: str | None = None,
        first_name: str | None = None,
        last_name: str | None = None,
        phone: str | None = None,
        gender: str | None = None,
        title: str | None = None,
        country_code: str | None = None,
        date_of_birth: str | None = None,
        loyalty_programs: Sequence[Mapping[str, Any]] | None = None,
        old_password: str | None = None,
        new_password: str | None = None,
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
        limit: int | None = None,
        cursor: str | None = None,
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

    async def create_users(  # noqa: WPS211
        self,
        first_name: str,
        last_name: str,
        password: str,
        email: str,
        phone: str,
    ) -> dict[str, Any]:
        body = {
            _DATA_KEY: {
                _TYPE_KEY: "users",
                _ATTRIBUTES_KEY: {
                    "firstName": first_name,
                    "lastName": last_name,
                    "email": email,
                    "password": password,
                    "phone": phone,
                },
            },
        }
        return await self._make_request(
            method=_METHOD_POST,
            url="/users",
            payload=body,
        )

    async def create_users_session(
        self,
        password: str,
        email: str,
    ) -> dict[str, Any]:
        body = {
            _DATA_KEY: {
                _TYPE_KEY: "user-sessions",
                _ATTRIBUTES_KEY: {"password": password, "email": email},
            },
        }
        return await self._make_request(
            method=_METHOD_POST,
            url="/users/sessions",
            payload=body,
        )

    async def create_verification_code(
        self,
        email: str,
    ) -> dict[str, Any]:
        body = {
            _DATA_KEY: {
                _TYPE_KEY: "verification-codes",
                _ATTRIBUTES_KEY: {"email": email},
            },
        }
        return await self._make_request(
            method=_METHOD_POST,
            url="/verification_code",
            payload=body,
        )

    async def update_password(
        self,
        email: str,
        password: str,
        user_id: str,
    ) -> dict[str, Any]:
        body = {
            _DATA_KEY: {
                _TYPE_KEY: "users",
                _ID_KEY: user_id,
                _ATTRIBUTES_KEY: {"password": password},
            },
        }
        return await self._make_request(
            method=_METHOD_PATCH,
            url="/users/{0}".format(email),
            payload=body,
        )

    async def update_user(  # noqa: WPS211
        self,
        email: str | None = None,
        first_name: str | None = None,
        last_name: str | None = None,
        phone: str | None = None,
        gender: str | None = None,
        title: str | None = None,
        country_code: str | None = None,
        date_of_birth: str | None = None,
        loyalty_programs: Sequence[Mapping[str, Any]] | None = None,
        old_password: str | None = None,
        new_password: str | None = None,
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
        for attr, attr_value in attributes.items():
            if attr_value is None:
                attributes.pop(attr)
        body = {
            _DATA_KEY: {
                _TYPE_KEY: "users",
                _ATTRIBUTES_KEY: attributes,
            },
        }
        return await self._make_request(
            method=_METHOD_PATCH,
            url="/users/{0}".format(email),
            payload=body,
        )

    async def create_trip_candidates_search(  # noqa: WPS211
        self,
        origin: tuple[float, float],
        destination: tuple[float, float],
        departure_after: datetime,
        passengers_dates_of_birth: Sequence[date],
        maximum_connections: int | None = None,
        allowed_segment_types: Sequence[LegType] | None = None,
    ) -> dict[str, Any]:
        attributes: dict[str, Any] = {
            _PASSENGERS_KEY: [
                {"dateOfBirth": dob.strftime("%Y-%m-%d")}
                for dob in passengers_dates_of_birth
            ],
            "criteria": [  # TODO: replace with _CRITERIA_KEY after #2178 MR merge
                {
                    "origin": {
                        "latitude": origin[0],
                        "longitude": origin[1],
                    },
                    "destination": {
                        "latitude": destination[0],
                        "longitude": destination[1],
                    },
                    "departureAfter": departure_after.isoformat(),
                },
            ],
        }
        if maximum_connections:
            attributes["criteria"][0]["maximumConnections"] = maximum_connections
        body = {
            _DATA_KEY: {
                _ATTRIBUTES_KEY: attributes,
                _TYPE_KEY: "trip-candidate-searches",
            },
        }
        if allowed_segment_types:
            body[_DATA_KEY][_RELATIONSHIPS_KEY] = {
                "allowedSegmentTypes": {
                    _DATA_KEY: [
                        {
                            _ID_KEY: leg_type.value,
                            "type": "leg-types",
                        }
                        for leg_type in allowed_segment_types
                    ],
                },
            }
        return await self._make_request(
            method=_METHOD_POST,
            url="/trip-candidates/searches",
            payload=body,
        )

    async def get_trip_candidate_search(
        self,
        trip_candidate_search: str,
    ) -> dict[str, Any]:
        return await self._make_request(
            method=_METHOD_GET,
            url="/trip-candidates/searches/{0}".format(
                trip_candidate_search,
            ),
        )

    async def list_trip_candidates_offers(
        self,
        trip_candidate_search_id: str,
    ) -> dict[str, Any]:
        return await self._make_request(
            method=_METHOD_GET,
            url="/trip-candidates/searches/{0}/offers".format(
                trip_candidate_search_id,
            ),
        )

    async def get_user(
        self,
    ) -> dict[str, Any]:
        return await self._make_request(
            method=_METHOD_GET,
            url="/users/me",
        )

    async def get_verification_code(
        self,
        email: str,
    ) -> dict[str, Any]:
        return await self._make_request(
            method=_METHOD_GET,
            url="/verification-code/{0}".format(email),
            query_parameters={
                _EMAIL_KEY: email,
            },
        )

    async def delete_user(
        self,
        password: str,
    ) -> dict[str, Any]:
        return await self._make_request(
            method=_METHOD_DELETE,
            url="/users/me",
            query_parameters={
                _PASSWORD_KEY: password,
            },
        )
