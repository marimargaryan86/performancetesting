import dataclasses
import datetime
import enum
from typing import Any, Literal, Mapping, Optional, Sequence, cast

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


trip_includes = Literal["segments", "segments.legs", "segments.legs.legType"]


class LegType(enum.Enum):
    air = "air"
    rail = "rail"


class _BaseClient(object):
    def __init__(
        self,
        api_url: str,
        token: str,
        client: Optional[httpx.AsyncClient] = None,
    ) -> None:
        self._api_url = api_url
        self._client = client or httpx.AsyncClient()
        self._client.base_url = httpx.URL(api_url)
        self._token = token

        self._client.headers.update(
            httpx.Headers(
                {
                    "Accept": "application/vnd.api+json",
                    "Authorization": "Bearer {0}".format(token),
                    "Content-Type": "application/vnd.api+json",
                },
            ),
        )

    async def _make_request(
        self,
        method: str,
        url: str,
        query_parameters: Optional[Mapping[str, Any]] = None,
        payload: Optional[Mapping[str, Any]] = None,
    ) -> dict[str, Any]:
        response = await self._client.request(
            method=method,
            url=url,
            params=query_parameters,
            json=payload,
        )

        response.raise_for_status()

        return response.json()


class LegsClient(_BaseClient):
    async def get_leg_by_id(self, leg_id: str) -> dict[str, Any]:
        return await self._make_request(
            method=_METHOD_GET,
            url="/legs/{0}".format(leg_id),
        )

    async def get_legs_types(self) -> dict[str, Any]:
        return await self._make_request(
            method=_METHOD_GET,
            url="/legs/types",
        )

    async def get_leg_type_by_id(self, leg_type_id: str) -> dict[str, Any]:
        return await self._make_request(
            method=_METHOD_GET,
            url="/legs/types/{0}".format(leg_type_id),
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

    async def get_legs_by_trip_id(self, trip_id: str) -> dict[str, Any]:
        return await self._make_request(
            method=_METHOD_GET,
            url="/trips/{0}/legs".format(trip_id),
        )

    async def get_legs_by_trip_search_id(self, trip_search_id: str) -> dict[str, Any]:
        return await self._make_request(
            method=_METHOD_GET,
            url="/trips/searches/{0}/legs".format(trip_search_id),
        )


class PlacesClient(_BaseClient):
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

    async def get_places_types(
        self,
        limit: Optional[int] = None,
        cursor: Optional[str] = None,
    ) -> dict[str, Any]:
        return await self._make_request(
            method=_METHOD_GET,
            url="/places/types",
            query_parameters=_make_pagination(limit, cursor),
        )

    async def get_places_type(
        self,
        place_type_id: str,
    ) -> dict[str, Any]:
        return await self._make_request(
            method=_METHOD_GET,
            url="/places/types/{0}".format(place_type_id),
        )


class SegmentsClient(_BaseClient):
    async def get_segment_by_id(self, segment_id: str) -> dict[str, Any]:
        return await self._make_request(
            method=_METHOD_GET,
            url="/segments/{0}".format(segment_id),
        )

    async def get_segments_by_trip(
        self,
        trip_id: str,
        limit: Optional[int] = None,
        cursor: Optional[str] = None,
    ) -> dict[str, Any]:
        return await self._make_request(
            method=_METHOD_GET,
            url="/trips/{0}/segments".format(trip_id),
            query_parameters=_make_pagination(limit, cursor),
        )

    async def get_segments_by_trip_search(
        self,
        trip_search_id: str,
        limit: Optional[int] = None,
        cursor: Optional[str] = None,
    ) -> dict[str, Any]:
        return await self._make_request(
            method=_METHOD_GET,
            url="/trips/searches/{0}/segments".format(trip_search_id),
            query_parameters=_make_pagination(limit, cursor),
        )


class TripsClient(_BaseClient):
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
        include: Optional[Sequence[trip_includes]] = None,
        limit: Optional[int] = None,
        cursor: Optional[str] = None,
    ) -> dict[str, Any]:
        query_parameters = cast(
            dict[str, int | str | Sequence[trip_includes]],
            _make_pagination(limit, cursor),
        )
        if include:
            query_parameters["include"] = include
        return await self._make_request(
            method=_METHOD_GET,
            url="/trips/searches/{0}/trips".format(trips_search_id),
            query_parameters=query_parameters,
        )


class JunctionClient(_BaseClient):  # noqa: WPS214
    def legs(self) -> LegsClient:
        return LegsClient(
            api_url=self._api_url,
            token=self._token,
            client=self._client,
        )

    def places(self) -> PlacesClient:
        return PlacesClient(
            api_url=self._api_url,
            token=self._token,
            client=self._client,
        )

    def segments(self) -> SegmentsClient:
        return SegmentsClient(
            api_url=self._api_url,
            token=self._token,
            client=self._client,
        )

    def trips(self) -> TripsClient:
        return TripsClient(
            api_url=self._api_url,
            token=self._token,
            client=self._client,
        )

    async def health(self) -> dict[str, Any]:
        return await self._make_request(
            method=_METHOD_GET,
            url="/health",
        )

    async def list_cabin_classes(self) -> dict[str, Any]:
        return await self._make_request(method=_METHOD_GET, url="/cabin-classes")

    async def get_cabin_class(
        self,
        cabin_class_id: str,
    ) -> dict[str, Any]:
        return await self._make_request(
            method=_METHOD_GET,
            url="/cabin-classes/{0}".format(cabin_class_id),
        )

    async def get_passenger_genders(
        self,
        limit: Optional[int] = None,
        cursor: Optional[str] = None,
    ) -> dict[str, Any]:
        return await self._make_request(
            method=_METHOD_GET,
            url="/passengers/genders",
            query_parameters=_make_pagination(limit, cursor),
        )

    async def get_passenger_gender(self, passenger_gender_id: str) -> dict[str, Any]:
        return await self._make_request(
            method=_METHOD_GET,
            url="/passengers/genders/{0}".format(passenger_gender_id),
        )

    async def get_passenger_titles(
        self,
        limit: Optional[int] = None,
        cursor: Optional[str] = None,
    ) -> dict[str, Any]:
        return await self._make_request(
            method=_METHOD_GET,
            url="/passengers/titles",
            query_parameters=_make_pagination(limit, cursor),
        )

    async def get_passenger_title(self, passenger_title_id: str) -> dict[str, Any]:
        return await self._make_request(
            method=_METHOD_GET,
            url="/passengers/titles/{0}".format(passenger_title_id),
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

    async def get_offers_by_offer_search_id(  # noqa: WPS211
        self,
        offers_search_id: str,
        cabin_class: Optional[Sequence[str]],
        include: Optional[Sequence[trip_includes]] = None,
        limit: Optional[int] = None,
        cursor: Optional[str] = None,
    ) -> dict[str, Any]:
        query_parameters = cast(
            dict[str, int | str | Sequence[str]],
            _make_pagination(limit, cursor),
        )
        if cabin_class:
            query_parameters["filter[groups.options.details.cabinClass]"] = cabin_class
        if include:
            query_parameters["include"] = include
        return await self._make_request(
            method=_METHOD_GET,
            url="/offers/searches/{0}/offers".format(offers_search_id),
            query_parameters=query_parameters,
        )

    async def get_offer_search(
        self,
        offers_search_id: str,
    ) -> dict[str, Any]:
        return await self._make_request(
            method=_METHOD_GET,
            url="/offers/searches/{0}".format(offers_search_id),
        )

    async def get_offer(
        self,
        offer_id: str,
    ) -> dict[str, Any]:
        return await self._make_request(
            method=_METHOD_GET,
            url="/offers/{0}".format(offer_id),
        )

    async def get_offer_groups_by_offer_group_id(
        self,
        offer_group_id: str,
    ) -> dict[str, Any]:
        return await self._make_request(
            method=_METHOD_GET,
            url="/offers/groups/{0}".format(offer_group_id),
        )

    async def get_offer_group_details(
        self,
        offer_group_details_id: str,
    ) -> dict[str, Any]:
        return await self._make_request(
            method=_METHOD_GET,
            url="/offers/groups/details/{0}".format(offer_group_details_id),
        )

    async def get_offer_options_by_offer_option_id(
        self,
        offer_option_id: str,
    ) -> dict[str, Any]:
        return await self._make_request(
            method=_METHOD_GET,
            url="/offers/options/{0}".format(offer_option_id),
        )

    async def get_offer_option_details(
        self,
        offer_option_details_id: str,
    ) -> dict[str, Any]:
        return await self._make_request(
            method=_METHOD_GET,
            url="/offers/options/details/{0}".format(offer_option_details_id),
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

    async def get_journeys(
        self,
        limit: Optional[int] = None,
        cursor: Optional[str] = None,
    ) -> dict[str, Any]:
        return await self._make_request(
            method=_METHOD_GET,
            url="/journeys",
            query_parameters=_make_pagination(limit, cursor),
        )

    async def get_journey_by_id(self, identifier: str) -> dict[str, Any]:
        return await self._make_request(
            method=_METHOD_GET,
            url="/journeys/{0}".format(identifier),
        )

    async def get_orders_by_journey_id(
        self,
        identifier: str,
        limit: Optional[int] = None,
        cursor: Optional[str] = None,
    ) -> dict[str, Any]:
        return await self._make_request(
            method=_METHOD_GET,
            url="/journeys/{0}/orders".format(identifier),
            query_parameters=_make_pagination(limit, cursor),
        )

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

    async def get_order_by_id(self, identifier: str) -> dict[str, Any]:
        response = await self._make_request(
            method=_METHOD_GET,
            url="/orders/{0}".format(identifier),
        )

        # todo: Use the real response instead.
        return await self._get_deprecated_order(response)

    async def get_bookings_by_order_id(
        self,
        identifier: str,
        limit: Optional[int] = None,
        cursor: Optional[str] = None,
    ) -> dict[str, Any]:
        return await self._make_request(
            method=_METHOD_GET,
            url="/orders/{0}/bookings".format(identifier),
            query_parameters=_make_pagination(limit, cursor),
        )

    async def get_booking_by_id(self, identifier: str) -> dict[str, Any]:
        return await self._make_request(
            method=_METHOD_GET,
            url="/bookings/{0}".format(identifier),
        )

    async def get_bookings_details_by_booking_id(
        self,
        identifier: str,
        limit: Optional[int] = None,
        cursor: Optional[str] = None,
    ) -> dict[str, Any]:
        return await self._make_request(
            method=_METHOD_GET,
            url="/bookings/{0}/details".format(identifier),
            query_parameters=_make_pagination(limit, cursor),
        )

    async def get_booking_details_by_id(self, identifier: str) -> dict[str, Any]:
        return await self._make_request(
            method=_METHOD_GET,
            url="/bookings/details/{0}".format(identifier),
        )

    async def get_search_offer_ids(
        self,
        offers_search_id: str,
    ) -> dict[str, Any]:
        return await self._make_request(
            method=_METHOD_GET,
            url="/offers/searches/{0}/offers".format(offers_search_id),
        )

    async def make_order_request(
        self,
        limit: Optional[int] = None,
        cursor: Optional[str] = None,
    ) -> dict[str, Any]:
        return await self._make_request(
            method=_METHOD_GET,
            url="/orders",
            query_parameters=_make_pagination(limit, cursor),
        )

    async def get_orders_id(
        self,
        orders_id: str,
    ) -> dict[str, Any]:
        return await self._make_request(
            method=_METHOD_GET,
            url="/orders/{0}".format(orders_id),
        )

    # todo: Delete.
    async def _get_deprecated_order(
        self,
        response: Mapping[str, Any],
    ) -> dict[str, Any]:
        bookings = await self.get_bookings_by_order_id(response[_DATA_KEY][_ID_KEY])
        journey = response[_DATA_KEY][_RELATIONSHIPS_KEY]["journey"]
        journey_response = await self.get_journey_by_id(journey[_DATA_KEY][_ID_KEY])
        journey_response[_DATA_KEY][_TYPE_KEY] = "orders"
        journey_response[_DATA_KEY][_ID_KEY] = response[_DATA_KEY][_ID_KEY]
        attributes = journey_response[_DATA_KEY][_ATTRIBUTES_KEY]
        attributes[_PASSENGERS_KEY] = response[_DATA_KEY][_ATTRIBUTES_KEY][
            _PASSENGERS_KEY
        ]
        attributes["orderResults"] = [
            {
                "orderId": booking[_RELATIONSHIPS_KEY]["order"][_DATA_KEY][_ID_KEY],
                "status": booking[_RELATIONSHIPS_KEY]["status"][_DATA_KEY][_ID_KEY],
            }
            for booking in bookings[_DATA_KEY]
        ]

        return journey_response


def _make_pagination(
    limit: Optional[int],
    cursor: Optional[str],
) -> dict[str, int | str]:
    return {
        key: pagination_value
        for key, pagination_value in ((_LIMIT_KEY, limit), (_CURSOR_KEY, cursor))
        if pagination_value
    }
