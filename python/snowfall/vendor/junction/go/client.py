import dataclasses
import datetime
import enum
from typing import Any, Literal, Mapping, Sequence, cast

from snowfall.vendor.junction import client as base_client
from snowfall.vendor.junction.go import models

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
_CRITERIA_KEY = "criteria"

trip_includes = Literal["segments", "segments.legs", "segments.legs.legType"]
offer_includes = Literal[
    "groups",
    "groups.details",
    "groups.details.legType",
    "groups.options",
    "groups.options.details",
    "groups.options.details.cabinClass",
    "groups.options.details.details",
]
offer_search_includes = Literal[
    "offers.groups",
    "offers.groups.details",
    "offers.groups.details.legType",
    "offers.groups.options",
    "offers.groups.options.details",
    "offers.groups.options.details.cabinClass",
    "offers.groups.options.details.details",
]
order_includes = Literal[
    "journey",
    "bookings",
    "bookings.details",
    "bookings.details.cabinClass",
    "bookings.details.legType",
]


class LegType(enum.Enum):
    air = "air"
    bus = "bus"
    ferry = "ferry"
    rail = "rail"


class _BaseClient(base_client.BaseClient):
    def __repr__(self) -> str:
        return "{cls}({url}".format(
            cls=self.__class__.__name__,
            url=self._base_url,
        )

    async def _make_request(
        self,
        method: str,
        url: str,
        query_parameters: Mapping[str, Any] | None = None,
        payload: Mapping[str, Any] | None = None,
    ) -> dict[str, Any]:
        response = await self.client.request(
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
        limit: int | None = None,
        cursor: str | None = None,
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
        limit: int | None = None,
        cursor: str | None = None,
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
        limit: int | None = None,
        cursor: str | None = None,
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
        limit: int | None = None,
        cursor: str | None = None,
    ) -> dict[str, Any]:
        return await self._make_request(
            method=_METHOD_GET,
            url="/trips/{0}/segments".format(trip_id),
            query_parameters=_make_pagination(limit, cursor),
        )

    async def get_segments_by_trip_search(
        self,
        trip_search_id: str,
        limit: int | None = None,
        cursor: str | None = None,
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
        allowed_segment_types: Sequence[LegType],
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
                    "allowedSegmentTypes": {
                        _DATA_KEY: [
                            {_ID_KEY: leg_type.value, "type": "leg-types"}
                            for leg_type in allowed_segment_types
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
        include: Sequence[trip_includes] | None = None,
        limit: int | None = None,
        cursor: str | None = None,
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

    async def create_trip_candidates_search(  # noqa: WPS211
        self,
        origin: tuple[float, float],
        destination: tuple[float, float],
        departure_after: datetime.datetime,
        passengers_dates_of_birth: Sequence[datetime.date],
        maximum_connections: int | None = None,
        allowed_segment_types: Sequence[LegType] | None = None,
    ) -> dict[str, Any]:
        attributes: dict[str, Any] = {
            _PASSENGERS_KEY: [
                {"dateOfBirth": dob.strftime("%Y-%m-%d")}
                for dob in passengers_dates_of_birth
            ],
            _CRITERIA_KEY: [
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
            attributes[_CRITERIA_KEY]["maximumConnections"] = maximum_connections
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
        trip_candidate_search_id: str,
    ) -> dict[str, Any]:
        return await self._make_request(
            method=_METHOD_GET,
            url="/trip-candidates/searches/{0}".format(trip_candidate_search_id),
        )

    async def get_trip_candidate_search_offers(
        self,
        trip_candidate_search_id: str,
    ) -> dict[str, Any]:
        return await self._make_request(
            method=_METHOD_GET,
            url="/trip-candidates/searches/{0}/offers".format(trip_candidate_search_id),
        )


class Client(_BaseClient):  # noqa: WPS214
    def legs(self) -> LegsClient:
        return LegsClient(base_url=str(self._base_url), client=self.client)

    def places(self) -> PlacesClient:
        return PlacesClient(base_url=str(self._base_url), client=self.client)

    def segments(self) -> SegmentsClient:
        return SegmentsClient(base_url=str(self._base_url), client=self.client)

    def trips(self) -> TripsClient:
        return TripsClient(base_url=str(self._base_url), client=self.client)

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
        limit: int | None = None,
        cursor: str | None = None,
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
        limit: int | None = None,
        cursor: str | None = None,
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
        session_token: str | None = None,
    ) -> dict[str, Any]:
        attributes: dict[str, Any] = {
            _PASSENGERS_KEY: [
                {"dateOfBirth": dob.isoformat()} for dob in passengers_dates_of_birth
            ],
        }

        if session_token:
            attributes["sessionToken"] = session_token

        body = {
            _DATA_KEY: {
                _ATTRIBUTES_KEY: attributes,
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
        cabin_class: Sequence[str] | None,
        include: Sequence[offer_includes] | None = None,
        limit: int | None = None,
        cursor: str | None = None,
    ) -> dict[str, Any]:
        query_parameters = cast(
            dict[str, int | str | Sequence[str]],
            _make_pagination(limit, cursor),
        )
        if cabin_class:
            query_parameters["filter[groups.options.details.cabinClass]"] = cabin_class
        if include:
            query_parameters["include"] = ",".join(include)
        return await self._make_request(
            method=_METHOD_GET,
            url="/offers/searches/{0}/offers".format(offers_search_id),
            query_parameters=query_parameters,
        )

    async def get_offer_search(
        self,
        offers_search_id: str,
        include: Sequence[offer_search_includes] | None = None,
    ) -> dict[str, Any]:
        query_parameters = {}
        if include:
            query_parameters["include"] = ",".join(include)
        return await self._make_request(
            method=_METHOD_GET,
            url="/offers/searches/{0}".format(offers_search_id),
            query_parameters=query_parameters,
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
        limit: int | None = None,
        cursor: str | None = None,
    ) -> dict[str, Any]:
        return await self._make_request(
            method=_METHOD_GET,
            url="offers/{0}/groups".format(offer_id),
            query_parameters=_make_pagination(limit, cursor),
        )

    async def get_offer_group_details_by_offer_group_id(
        self,
        offer_group_id: str,
        limit: int | None = None,
        cursor: str | None = None,
    ) -> dict[str, Any]:
        return await self._make_request(
            method=_METHOD_GET,
            url="/offers/groups/{0}/details".format(offer_group_id),
            query_parameters=_make_pagination(limit, cursor),
        )

    async def get_offer_options_by_offer_group_id(
        self,
        offer_group_id: str,
        limit: int | None = None,
        cursor: str | None = None,
    ) -> dict[str, Any]:
        return await self._make_request(
            method=_METHOD_GET,
            url="/offers/groups/{0}/options".format(offer_group_id),
            query_parameters=_make_pagination(limit, cursor),
        )

    async def get_offer_option_details_by_offer_option_id(
        self,
        offer_option_id: str,
        limit: int | None = None,
        cursor: str | None = None,
    ) -> dict[str, Any]:
        return await self._make_request(
            method=_METHOD_GET,
            url="/offers/options/{0}/details".format(offer_option_id),
            query_parameters=_make_pagination(limit, cursor),
        )

    async def create_offer_quote(
        self,
        offer_id: str,
        option_ids: Sequence[str],
        session_token: str | None = None,
    ) -> dict[str, Any]:
        body = {
            _DATA_KEY: {
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
                _TYPE_KEY: "trip-offer-price-quotes",
            },
        }
        if session_token:
            body[_DATA_KEY][_ATTRIBUTES_KEY] = {"sessionToken": session_token}
        else:
            body[_DATA_KEY][_ATTRIBUTES_KEY] = {}
        return await self._make_request(
            method=_METHOD_POST,
            url="/offers/quotes",
            payload=body,
        )

    async def get_offer_quote_by_id(self, identifier: str) -> dict[str, Any]:
        return await self._make_request(
            method=_METHOD_GET,
            url="/offers/quotes/{0}".format(identifier),
        )

    async def get_journeys(
        self,
        limit: int | None = None,
        cursor: str | None = None,
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
        limit: int | None = None,
        cursor: str | None = None,
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

    async def create_order(  # noqa: WPS211
        self,
        quote_id: str,
        passengers: Sequence[models.Passenger],
        contact_details: models.ContactDetails,
        residence_address: models.Address | None = None,
        include: Sequence[order_includes] | None = None,
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
                    "residenceAddress": (
                        dataclasses.asdict(
                            residence_address,
                            dict_factory=models.dict_factory_to_camel,
                        )
                        if residence_address
                        else None
                    ),
                },
                _RELATIONSHIPS_KEY: {
                    "quote": {
                        _DATA_KEY: {
                            _ID_KEY: quote_id,
                            _TYPE_KEY: "trip-offer-price-quotes",
                        },
                    },
                },
                _TYPE_KEY: "orders",
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

    async def get_order_by_id(
        self,
        identifier: str,
        include: Sequence[order_includes] | None = None,
    ) -> dict[str, Any]:
        query_parameters: dict[str, str] = {}
        if include:
            query_parameters["include"] = ",".join(include)
        return await self._make_request(
            method=_METHOD_GET,
            url="/orders/{0}".format(identifier),
            query_parameters=query_parameters,
        )

    async def get_bookings_by_order_id(
        self,
        identifier: str,
        limit: int | None = None,
        cursor: str | None = None,
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

    async def get_booking_details_by_booking_id(
        self,
        identifier: str,
        limit: int | None = None,
        cursor: str | None = None,
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
        limit: int | None = None,
        cursor: str | None = None,
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


def _make_pagination(
    limit: int | None,
    cursor: str | None,
) -> dict[str, int | str]:
    return {
        key: pagination_value
        for key, pagination_value in ((_LIMIT_KEY, limit), (_CURSOR_KEY, cursor))
        if pagination_value
    }
