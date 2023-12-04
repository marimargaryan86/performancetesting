import dataclasses
import json
import logging
from collections.abc import Mapping, Sequence
from datetime import date, datetime
from itertools import starmap
from typing import Any, Literal, TypeAlias

import httpx

from snowfall.vendor.junction.client import make_pagination_params
from snowfall.vendor.junction.go import models
from snowfall.vendor.junction.go.client import Client, LegType

logger = logging.getLogger()

_OrderIncludes: TypeAlias = Literal[
    "journey",
    "bookings",
    "bookings.details",
    "bookings.details.cabinClass",
    "bookings.details.legType",
]
_OfferSearchIncludes: TypeAlias = Literal[
    "offers.groups",
    "offers.groups.details",
    "offers.groups.details.legType",
    "offers.groups.options",
    "offers.groups.options.details",
    "offers.groups.options.details.cabinClass",
    "offers.groups.options.details.details",
]

_DATA_KEY = "data"
_ID_KEY = "id"
_TYPE_KEY = "type"
_RELATIONSHIPS_KEY = "relationships"
_ATTRIBUTES_KEY = "attributes"
_PASSENGERS_KEY = "passengers"
_METHOD_GET = "GET"
_METHOD_POST = "POST"
_METHOD_PATCH = "PATCH"
_METHOD_DELETE = "DELETE"
_EMAIL_KEY = "email"
_CRITERIA_KEY = "criteria"
_CONTACT_DETAILS_KEY = "contactDetails"
_RESIDENCE_ADDRESS_KEY = "residenceAddress"
_ADDRESS_KEY = "address"


class MobileApiClient(Client):
    def __init__(
        self,
        base_url: str,
        auth: httpx.Auth | None = None,
        client: httpx.AsyncClient | None = None,
    ):
        super().__init__(base_url=base_url, auth=auth, client=client)
        self.logger = logging.getLogger()
        self.logger.setLevel(logging.DEBUG)

    def generate_curl_command(
        self,
        method: str,
        url: str,
        query_parameters: Mapping[str, str] | None = None,
        body: Mapping[str, Any] | None = None,
        headers: Mapping[str, str] | None = None,
    ) -> str:
        full_url = str(self._base_url) + url
        curl_command = 'curl -X "{0}" "{1}"'.format(method, full_url)

        if query_parameters:
            curl_command += ' -d "{0}"'.format(json.dumps(query_parameters))
        if headers:
            header_strings = list(starmap('-H "{0}: {1}"'.format, headers.items()))
            curl_command += " ".join(header_strings)

        if body:
            curl_command += " -H \"Content-Type: application/json\" -d '{0}'".format(
                json.dumps(body),
            )

        return "Curl command for the {0} request:\n{1}".format(method, curl_command)

    async def list_cabin_classes(self) -> dict[str, Any]:
        return await self._make_request(method=_METHOD_GET, url="/cabin-classes")

    async def create_payment(
        self,
        currency: str,
        amount: str,
    ) -> dict[str, Any]:
        body = {
            _DATA_KEY: {
                _ATTRIBUTES_KEY: {
                    "amount": amount,
                    "currency": currency,
                },
                _TYPE_KEY: "payments",
            },
        }
        self.logger.info(
            "create_payment: %s",  # noqa: WPS323
            json.dumps(body, indent=4),
        )
        return await self._make_request(
            method=_METHOD_POST,
            url="/payments",
            payload=body,
        )

    async def update_payment(
        self,
        payment_intent_id: str,
        voucher_id: str,
    ) -> dict[str, Any]:
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
        return await self._make_request(
            method=_METHOD_PATCH,
            url="/payments/{0}".format(payment_intent_id),
            payload=body,
        )

    async def create_order(
        self,
        quote_id: str,
        passengers: Sequence[models.Passenger],
        contact_details: models.ContactDetails,
        residence_address: models.Address | None = None,
        include: Sequence[_OrderIncludes] | None = None,
    ) -> dict[str, Any]:
        raise RuntimeError(
            "This client cannot create orders without payments. "
            "Please, use create_order_with_payments",
        )

    async def create_offer_price_quote(
        self,
        offer_id: str,
        option_ids: Sequence[str],
    ) -> dict[str, Any]:
        options_data = [
            {"id": option_id, "type": "offer-options"} for option_id in option_ids
        ]

        body = {
            _DATA_KEY: {
                _TYPE_KEY: "trip-offer-price-quotes",
                _ATTRIBUTES_KEY: {"sessionToken": "FMSXrOAhIOdvIbxAmfSt7vJtRBkurNbn"},
                _RELATIONSHIPS_KEY: {
                    "offer": {
                        _DATA_KEY: {
                            _ID_KEY: offer_id,
                            _TYPE_KEY: "offers",
                        },
                    },
                    "options": {
                        _DATA_KEY: options_data,
                    },
                },
            },
        }
        return await self._make_request(
            method=_METHOD_POST,
            url="/offers/quotes",
            payload=body,
        )

    async def get_offer_price_quote(
        self,
        offer_price_quote_id: str,
    ) -> dict[str, Any]:
        return await self._make_request(
            method=_METHOD_GET,
            url="/offers/quotes/{0}".format(offer_price_quote_id),
        )

    async def create_order_with_payment(
        self,
        quote_id: str,
        passengers: Sequence[models.Passenger],
        contact_details: models.ContactDetails,
        address: models.Address,
        payment_id: str,
        voucher_id: str | None = None,
        include: Sequence[_OrderIncludes] | None = None,
    ) -> dict[str, Any]:
        body: dict[str, dict[str, Any]]
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
                    _CONTACT_DETAILS_KEY: dataclasses.asdict(
                        contact_details,
                        dict_factory=models.dict_factory_to_camel,
                    ),
                    _ADDRESS_KEY: dataclasses.asdict(
                        address,
                        dict_factory=models.dict_factory_to_camel,
                    ),
                },
                _RELATIONSHIPS_KEY: {
                    "payment": {
                        _DATA_KEY: {_TYPE_KEY: "payments", _ID_KEY: payment_id},
                    },
                    "quote": {
                        _DATA_KEY: {
                            _TYPE_KEY: "trip-offer-price-quotes",
                            _ID_KEY: quote_id,
                        },
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

    async def add_user_group_member(
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

    async def update_user_group_member(
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
            query_parameters=make_pagination_params(limit, cursor),
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

    async def list_offers_by_offer_search(
        self,
        offer_search_id: str,
    ) -> dict[str, Any]:
        url = "/offers/searches/{0}/offers".format(offer_search_id)
        query_parameters = {"include": "groups.details"}

        curl_command = self.generate_curl_command(
            _METHOD_GET,
            url,
            query_parameters=query_parameters,
        )
        self.logger.info(curl_command)

        return await self._make_request(
            method=_METHOD_GET,
            url=url,
            query_parameters=query_parameters,
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

    async def create_users(
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

    async def update_user(
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
                "password": password,
            },
        )

    async def get_places(self, name: str) -> dict[str, Any]:
        query_parameters = {
            "query[name]": name,
        }
        url = "/places"
        curl_command = self.generate_curl_command(
            _METHOD_GET,
            "/places",
            query_parameters,
        )
        self.logger.info(curl_command)
        return await self._make_request(
            method=_METHOD_GET,
            url=url,
            query_parameters=query_parameters,
        )

    async def create_trip_search(
        self,
        origin_id: str,
        destination_id: str,
        departure_after: datetime,
    ) -> dict[str, Any]:
        url = "/trips/searches"
        body = {
            "data": {
                "attributes": {
                    "departureAfter": departure_after,
                },
                "relationships": {
                    "origin": {"data": {"id": origin_id, "type": "places"}},
                    "destination": {
                        "data": {"id": destination_id, "type": "places"},
                    },
                },
                "type": "trip-searches",
            },
        }

        curl_command = self.generate_curl_command(
            _METHOD_POST,
            url,
            body=body,
        )
        self.logger.info(curl_command)
        return await self._make_request(
            method=_METHOD_POST,
            url=url,
            payload=body,
        )

    async def get_trips_list(
        self,
        trips_search_id: str,
    ) -> dict[str, Any]:
        url = "/trips/searches/{0}/trips".format(trips_search_id)
        curl_command = self.generate_curl_command(
            _METHOD_GET,
            url,
        )
        self.logger.info(curl_command)
        return await self._make_request(
            method=_METHOD_GET,
            url=url,
        )

    async def create_offers_search(
        self,
        trip_id: str,
        passengers_dates_of_birth: Sequence[date],
    ) -> dict[str, Any]:
        url = "/offers/searches"
        attributes: dict[str, Any] = {
            "passengers": [
                {"dateOfBirth": dob.isoformat()} for dob in passengers_dates_of_birth
            ],
        }

        body = {
            "data": {
                "attributes": attributes,
                "relationships": {
                    "trips": {
                        "data": [
                            {"id": trip_id, "type": "trips"},
                        ],
                    },
                },
                "type": "trip-offer-searches",
            },
        }
        headers = {
            "Session-Token": "YMSXrOAhIOdvIbxAmfSt7vJtRBkurNb6",
        }
        curl_command = self.generate_curl_command(
            _METHOD_POST,
            url,
            headers=headers,
            body=body,
        )
        self.logger.info(curl_command)
        return await self._make_request(
            method=_METHOD_POST,
            url=url,
            headers=headers,
            payload=body,
        )

    async def create_trip_candidates_search(
        self,
        origin: tuple[float, float],
        destination: tuple[float, float],
        departure_after: datetime,
        passengers_dates_of_birth: Sequence[date],
        maximum_connections: int | None = None,
        allowed_segment_types: Sequence[LegType] | None = None,
    ) -> dict[str, Any]:
        passengers = [
            {"dateOfBirth": dob.strftime("%Y-%m-%d")}
            for dob in passengers_dates_of_birth
        ]

        sessiontoken = "FMSXrOAhIOdvIbxAmfSt7vJtRBkurNbn"
        criteria = [
            {
                "origin": {
                    "latitude": origin[0],
                    "longitude": origin[1],
                },
                "destination": {
                    "latitude": destination[0],
                    "longitude": destination[1],
                },
                "departureAfter": departure_after,
            },
        ]

        if maximum_connections is not None:
            criteria[0]["maximumConnections"] = maximum_connections

        body_data = {
            "type": "trip-candidate-searches",
            "attributes": {
                "sessionToken": sessiontoken,
                "criteria": criteria,
                "passengers": passengers,
            },
        }

        if allowed_segment_types:
            body_data["relationships"] = {
                "allowedSegmentTypes": {
                    "data": [
                        {
                            "id": leg_type.value,
                            "type": "leg-types",
                        }
                        for leg_type in allowed_segment_types
                    ],
                },
            }

        body = {
            "data": body_data,
        }
        url = "/trip-candidates/searches"
        curl_command = self.generate_curl_command(
            _METHOD_POST,
            url=url,
            body=body,
        )
        logger.info(curl_command)
        return await self._make_request(
            method=_METHOD_POST,
            url=url,
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
        url = "/trip-candidates/searches/{0}/offers".format(trip_candidate_search_id)

        query_parameters = {"include": "groups.details"}

        curl_command = self.generate_curl_command(
            _METHOD_GET,
            url=url,
            query_parameters=query_parameters,
        )
        logger.info(curl_command)

        return await self._make_request(
            method=_METHOD_GET,
            url=url,
            query_parameters=query_parameters,
        )

    async def get_offer_search(
        self,
        offers_search_id: str,
        include: Sequence[_OfferSearchIncludes] | None = None,
    ) -> dict[str, Any]:
        query_parameters = {}

        if include:
            query_parameters["include"] = ",".join(include)
        return await self._make_request(
            method=_METHOD_GET,
            url="/offers/searches/{0}".format(offers_search_id),
            query_parameters=query_parameters,
        )

    async def create_offer_simple_search(
        self,
        origin: tuple[float, float],
        destination: tuple[float, float],
        departure_after: datetime,
        passengers_dates_of_birth: Sequence[date],
        maximum_connections: int | None = None,
        allowed_segment_types: Sequence[LegType] | None = None,
    ) -> dict[str, Any]:
        passengers = [
            {"dateOfBirth": dob.strftime("%Y-%m-%d")}
            for dob in passengers_dates_of_birth
        ]

        sessiontoken = "FMSXrOAhIOdvIbxAmfSt7vJtRBkurNbn"
        criteria = {
            "origin": {
                "latitude": origin[0],
                "longitude": origin[1],
            },
            "destination": {
                "latitude": destination[0],
                "longitude": destination[1],
            },
            "departureAfter": departure_after,
        }

        if maximum_connections is not None:
            criteria["maximumConnections"] = maximum_connections

        body_data = {
            "type": "simple-offer-searches",
            "attributes": {
                "sessionToken": sessiontoken,
                "criteria": criteria,
                "passengers": passengers,
            },
        }

        if allowed_segment_types:
            body_data["relationships"] = {
                "allowedSegmentTypes": {
                    "data": [
                        {
                            "id": leg_type.value,
                            "type": "leg-types",
                        }
                        for leg_type in allowed_segment_types
                    ],
                },
            }

        body = {
            "data": body_data,
        }
        url = "/simple-offers/searches"
        curl_command = self.generate_curl_command(
            _METHOD_POST,
            url,
            body=body,
        )
        logger.info(curl_command)
        return await self._make_request(
            method=_METHOD_POST,
            url=url,
            payload=body,
        )

    async def list_offers_simple_search(
        self,
        offer_simple_search_id: str,
    ) -> dict[str, Any]:
        url = "/offers/searches/{0}/offers".format(offer_simple_search_id)
        query_parameters = {"include": "groups.details"}

        curl_command = self.generate_curl_command(
            _METHOD_GET,
            url=url,
            query_parameters=query_parameters,
        )
        logger.info(curl_command)

        return await self._make_request(
            method=_METHOD_GET,
            url=url,
            query_parameters=query_parameters,
        )
