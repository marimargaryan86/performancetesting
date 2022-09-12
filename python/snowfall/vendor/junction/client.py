import dataclasses
import datetime
import enum
from typing import Any, Mapping, Optional, Sequence, Union

import httpx

from snowfall.vendor.junction import models

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


class LegType(enum.Enum):
    air = "air"
    rail = "rail"


class JunctionClient(object):  # noqa: WPS214
    def __init__(
        self,
        api_url: str,
        token: str,
        client: Optional[httpx.AsyncClient] = None,
    ) -> None:
        self._api_url = api_url
        self._token = token
        self._client = client or httpx.AsyncClient()

    async def health(self) -> dict[str, Any]:
        return await self._make_request(
            method=_METHOD_GET,
            url="/health",
        )

    async def list_places(
        self,
        limit: Optional[int] = None,
        cursor: Optional[str] = None,
    ) -> dict[str, Any]:
        return await self._make_request(
            method=_METHOD_GET,
            url="/places",
            query_parameters=_make_pagination(limit, cursor),
        )

    async def get_place_by_id(self, place_id: str) -> dict[str, Any]:
        return await self._make_request(
            method=_METHOD_GET,
            url="/places/{0}".format(place_id),
        )

    async def get_leg_by_id(self, leg_id: str) -> dict[str, Any]:
        return await self._make_request(
            method=_METHOD_GET,
            url="/legs/{0}".format(leg_id),
        )

    async def get_legs_by_segment_id(
        self,
        segment_id: str,
        limit: Optional[int] = None,
        cursor: Optional[str] = None,
    ) -> dict[str, Any]:
        return await self._make_request(
            method=_METHOD_GET,
            url="/segments/{0}/legs".format(segment_id),
            query_parameters=_make_pagination(limit, cursor),
        )

    async def get_segment_by_id(self, segment_id: str) -> dict[str, Any]:
        return await self._make_request(
            method=_METHOD_GET,
            url="/segments/{0}".format(segment_id),
        )

    async def get_trip_by_id(self, trip_id: str) -> dict[str, Any]:
        return await self._make_request(
            method=_METHOD_GET,
            url="/trips/{0}".format(trip_id),
        )

    async def create_trip_search(
        self,
        origin_id: str,
        destination_id: str,
        departure_after: datetime.datetime,
        leg_types: Sequence[LegType],
    ) -> dict[str, Any]:
        body = {
            _DATA_KEY: {
                _ATTRIBUTES_KEY: {
                    "departureAfter": departure_after.isoformat(),
                },
                _RELATIONSHIPS_KEY: {
                    "origin": {_DATA_KEY: {_ID_KEY: origin_id, _TYPE_KEY: "places"}},
                    "destination": {
                        _DATA_KEY: {_ID_KEY: destination_id, _TYPE_KEY: "places"},
                    },
                    "legTypes": {
                        _DATA_KEY: [
                            {_ID_KEY: leg_type.value, "type": "leg-types"}
                            for leg_type in leg_types
                        ],
                    },
                },
                _TYPE_KEY: "trip-searches",
            },
        }
        return await self._make_request(
            method=_METHOD_POST,
            url="/trips/searches",
            payload=body,
        )

    async def get_trip_search_by_id(self, trips_search_id: str) -> dict[str, Any]:
        return await self._make_request(
            method=_METHOD_GET,
            url="/trips/searches/{0}".format(trips_search_id),
        )

    async def get_trips_by_trip_search_id(
        self,
        trips_search_id: str,
        limit: Optional[int] = None,
        cursor: Optional[str] = None,
    ) -> dict[str, Any]:
        return await self._make_request(
            method=_METHOD_GET,
            url="/trips/searches/{0}/trips".format(trips_search_id),
            query_parameters=_make_pagination(limit, cursor),
        )

    async def create_offer_search(
        self,
        trip_ids: Sequence[str],
        passengers_dates_of_birth: Sequence[datetime.date],
    ) -> dict[str, Any]:
        body = {
            _DATA_KEY: {
                _ATTRIBUTES_KEY: {
                    _PASSENGERS_KEY: [
                        {"dateOfBirth": dob.isoformat()}
                        for dob in passengers_dates_of_birth
                    ],
                },
                _RELATIONSHIPS_KEY: {
                    "trips": {
                        _DATA_KEY: [
                            {_ID_KEY: trip_id, _TYPE_KEY: "trips"}
                            for trip_id in trip_ids
                        ],
                    },
                },
                _TYPE_KEY: "trip-offer-searches",
            },
        }
        return await self._make_request(
            method=_METHOD_POST,
            url="/offers/searches",
            payload=body,
        )

    async def get_offers_by_offer_search_id(
        self,
        offers_search_id: str,
        cabin_class: Optional[Sequence[str]],
        limit: Optional[int] = None,
        cursor: Optional[str] = None,
    ) -> dict[str, Any]:
        pagination_parameters = _make_pagination(limit, cursor)
        query_parameters: dict[str, int | str | Sequence[str]] = {
            parameter: pagination_parameters[parameter]
            for parameter in pagination_parameters
        }
        if cabin_class:
            query_parameters["filter[groups.options.details.cabinClass]"] = cabin_class
        return await self._make_request(
            method=_METHOD_GET,
            url="/offers/searches/{0}/offers".format(offers_search_id),
            query_parameters=query_parameters,
        )

    async def get_offer_groups_by_offer_id(
        self,
        offer_id: str,
        limit: Optional[int] = None,
        cursor: Optional[str] = None,
    ) -> dict[str, Any]:
        return await self._make_request(
            method=_METHOD_GET,
            url="offers/{0}/groups".format(offer_id),
            query_parameters=_make_pagination(limit, cursor),
        )

    async def get_offer_group_details_by_offer_group_id(
        self,
        offer_group_id: str,
        limit: Optional[int] = None,
        cursor: Optional[str] = None,
    ) -> dict[str, Any]:
        return await self._make_request(
            method=_METHOD_GET,
            url="/offers/groups/{0}/details".format(offer_group_id),
            query_parameters=_make_pagination(limit, cursor),
        )

    async def get_offer_options_by_offer_group_id(
        self,
        offer_group_id: str,
        limit: Optional[int] = None,
        cursor: Optional[str] = None,
    ) -> dict[str, Any]:
        return await self._make_request(
            method=_METHOD_GET,
            url="/offers/groups/{0}/options".format(offer_group_id),
            query_parameters=_make_pagination(limit, cursor),
        )

    async def get_offer_option_details_by_offer_option_id(
        self,
        offer_option_id: str,
        limit: Optional[int] = None,
        cursor: Optional[str] = None,
    ) -> dict[str, Any]:
        return await self._make_request(
            method=_METHOD_GET,
            url="/offers/options/{0}/details".format(offer_option_id),
            query_parameters=_make_pagination(limit, cursor),
        )

    async def create_order(
        self,
        offer_id: str,
        option_ids: Sequence[str],
        passengers: Sequence[models.Passenger],
        contact_details: models.ContactDetails,
    ) -> dict[str, Any]:
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
                },
                _TYPE_KEY: "orders",
            },
        }

        response = await self._make_request(
            method=_METHOD_POST,
            url="/orders",
            payload=body,
        )

        # todo: Use the real response instead.
        return await self._get_deprecated_order(response)

    async def add_order_to_journey(
        self,
        journey_id: str,
        offer_aggregate_id: str,
        offer_ids: Sequence[str],
        passengers: Sequence[models.Passenger],
    ) -> dict[str, Any]:
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
                },
                _RELATIONSHIPS_KEY: {
                    "offer": {
                        _DATA_KEY: {
                            _ID_KEY: offer_aggregate_id,
                            _TYPE_KEY: "offers",
                        },
                    },
                    "options": {
                        _DATA_KEY: [
                            {
                                _ID_KEY: offer_id,
                                _TYPE_KEY: "offer-options",
                            }
                            for offer_id in offer_ids
                        ],
                    },
                },
                _TYPE_KEY: "orders",
            },
        }

        return await self._make_request(
            method=_METHOD_POST,
            url="/journeys/{0}/orders".format(journey_id),
            payload=body,
        )

    async def get_journeys(
        self,
        limit: Optional[int] = None,
        cursor: Optional[str] = None,
    ) -> dict[str, Any]:
        return await self._make_request(
            method=_METHOD_GET,
            url="journeys",
            query_parameters=_make_pagination(limit, cursor),
        )

    async def get_journey_by_id(self, identifier: str) -> dict[str, Any]:
        return await self._make_request(
            method=_METHOD_GET,
            url="/journeys/{0}".format(identifier),
        )

    async def get_order_by_id(self, identifier: str) -> dict[str, Any]:
        response = await self._make_request(
            method=_METHOD_GET,
            url="journeys/orders/{0}".format(identifier),
        )

        # todo: Use the real response instead.
        return await self._get_deprecated_order(response)

    async def get_orders_by_journey_id(
        self,
        identifier: str,
        limit: Optional[int] = None,
        cursor: Optional[str] = None,
    ) -> dict[str, Any]:
        return await self._make_request(
            method=_METHOD_GET,
            url="journeys/{0}/orders".format(identifier),
            query_parameters=_make_pagination(limit, cursor),
        )

    async def get_booking_by_id(self, identifier: str) -> dict[str, Any]:
        return await self._make_request(
            method=_METHOD_GET,
            url="journeys/bookings/{0}".format(identifier),
        )

    async def get_bookings_by_order_id(
        self,
        identifier: str,
        limit: Optional[int] = None,
        cursor: Optional[str] = None,
    ) -> dict[str, Any]:
        return await self._make_request(
            method=_METHOD_GET,
            url="journeys/orders/{0}/bookings".format(identifier),
            query_parameters=_make_pagination(limit, cursor),
        )

    # todo: Delete.
    async def _get_deprecated_order(
        self,
        response: Mapping[str, Any],
    ) -> dict[str, Any]:
        bookings = await self.get_bookings_by_order_id(
            response[_DATA_KEY][_ATTRIBUTES_KEY][_ID_KEY],
        )
        journey = response[_DATA_KEY][_RELATIONSHIPS_KEY]["journey"]
        journey_response = await self.get_journey_by_id(journey[_DATA_KEY][_ID_KEY])
        journey_response[_DATA_KEY][_TYPE_KEY] = "orders"
        attributes = journey_response[_DATA_KEY][_ATTRIBUTES_KEY]
        attributes.pop("journeyReference")
        attributes[_PASSENGERS_KEY] = response[_DATA_KEY][_ATTRIBUTES_KEY][
            _PASSENGERS_KEY
        ]
        attributes["orderResults"] = [
            {
                "status": booking[_RELATIONSHIPS_KEY]["status"][_DATA_KEY][_ID_KEY],
            }
            for booking in bookings[_DATA_KEY]
        ]

        return journey_response

    async def _make_request(
        self,
        method: str,
        url: str,
        query_parameters: Optional[Mapping[str, Any]] = None,
        payload: Optional[Mapping[str, Any]] = None,
    ) -> dict[str, Any]:
        headers = {
            "Authorization": "Bearer {0}".format(self._token),
        }

        if payload:
            headers["Content-Type"] = "application/vnd.api+json"

        response = await self._client.request(
            method=method,
            headers=headers,
            url="{0}/{1}".format(self._api_url, url.lstrip("/")),
            params=query_parameters,
            json=payload,
        )

        response.raise_for_status()

        return response.json()


def _make_pagination(
    limit: Optional[int],
    cursor: Optional[str],
) -> dict[str, Union[int, str]]:
    return {
        key: pagination_value
        for key, pagination_value in ((_LIMIT_KEY, limit), (_CURSOR_KEY, cursor))
        if pagination_value
    }
