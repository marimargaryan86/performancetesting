import dataclasses
import datetime
from typing import Any, Dict, Optional, Sequence

import requests

from snowfall.vendor.junction import models

_DATA_KEY = "data"
_TYPE_KEY = "type"


class JunctionClient(object):  # noqa: WPS214

    _post_headers = {
        "Content-Type": "application/vnd.api+json",
    }

    def __init__(
        self,
        api_url: str,
        token: str,
        client: Optional[requests.sessions.Session] = None,
    ) -> None:
        self._api_url = api_url
        self._token = token
        self._client = client or requests.session()

    def health(self) -> Dict[str, Any]:
        response = self._client.get(
            "{0}/health".format(self._api_url),
        )

        response.raise_for_status()

        return response.json()

    def list_places(
        self,
        limit: Optional[int] = None,
        cursor: Optional[str] = None,
    ) -> Dict[str, Any]:
        request_parameters = {
            key: vl for key, vl in (("limit", limit), ("cursor", cursor)) if vl
        }
        response = self._client.get(
            "{0}/places".format(self._api_url),
            headers=self._auth_headers,
            params=request_parameters,
        )

        response.raise_for_status()

        return response.json()

    def get_place_by_id(self, place_id: str) -> Dict[str, Any]:
        response = self._client.get(
            "{0}/places/{1}".format(self._api_url, place_id),
            headers=self._auth_headers,
        )

        response.raise_for_status()

        return response.json()

    def get_leg_by_id(self, leg_id: str) -> Dict[str, Any]:
        response = self._client.get(
            "{0}/legs/{1}".format(self._api_url, leg_id),
            headers=self._auth_headers,
        )

        response.raise_for_status()

        return response.json()

    def get_segment_by_id(self, segment_id: str) -> Dict[str, Any]:
        response = self._client.get(
            "{0}/segments/{1}".format(self._api_url, segment_id),
            headers=self._auth_headers,
        )

        response.raise_for_status()

        return response.json()

    def get_trip_by_id(self, trip_id: str) -> Dict[str, Any]:
        response = self._client.get(
            "{0}/trips/{1}".format(self._api_url, trip_id),
            headers=self._auth_headers,
        )

        response.raise_for_status()

        return response.json()

    def create_trip_search(
        self,
        origin_id: str,
        destination_id: str,
        departure_after: datetime.datetime,
    ) -> Dict[str, Any]:
        body = {
            _DATA_KEY: {
                "attributes": {
                    "departureAfter": departure_after.isoformat(),
                },
                "relationships": {
                    "origin": {_DATA_KEY: {"id": origin_id, _TYPE_KEY: "places"}},
                    "destination": {
                        _DATA_KEY: {"id": destination_id, _TYPE_KEY: "places"},
                    },
                },
                _TYPE_KEY: "trip-searches",
            },
        }
        response = self._client.post(
            "{0}/trips/searches".format(self._api_url),
            headers=dict(self._auth_headers, **self._post_headers),
            json=body,
        )

        response.raise_for_status()

        return response.json()

    def get_trip_search_by_id(self, trips_search_id: str) -> Dict[str, Any]:
        response = self._client.get(
            "{0}/trips/searches/{1}".format(self._api_url, trips_search_id),
            headers=self._auth_headers,
        )

        response.raise_for_status()

        return response.json()

    def get_trips_by_trip_search_id(self, trips_search_id: str) -> Dict[str, Any]:
        response = self._client.get(
            "{0}/trips/searches/{1}/trips".format(self._api_url, trips_search_id),
            headers=self._auth_headers,
        )

        response.raise_for_status()

        return response.json()

    def create_offer_search(
        self,
        trip_ids: Sequence[str],
        passengers_dates_of_birth: Sequence[datetime.date],
    ) -> Dict[str, Any]:
        body = {
            _DATA_KEY: {
                "attributes": {
                    "passengers": [
                        {"dateOfBirth": dob.isoformat()}
                        for dob in passengers_dates_of_birth
                    ],
                },
                "relationships": {
                    "trips": {
                        _DATA_KEY: [
                            {"id": trip_id, _TYPE_KEY: "trips"} for trip_id in trip_ids
                        ],
                    },
                },
                _TYPE_KEY: "trip-offer-searches",
            },
        }
        response = self._client.post(
            "{0}/offers/searches".format(self._api_url),
            headers=dict(self._auth_headers, **self._post_headers),
            json=body,
        )

        response.raise_for_status()

        return response.json()

    def get_offers_by_offer_search_id(self, offers_search_id: str) -> Dict[str, Any]:
        response = self._client.get(
            "{0}/offers/searches/{1}/offers".format(self._api_url, offers_search_id),
            headers=self._auth_headers,
        )

        response.raise_for_status()

        return response.json()

    def create_order(
        self,
        offer_aggregate_id: str,
        offer_ids: Sequence[str],
        passengers: Sequence[models.Passenger],
        contact_details: models.ContactDetails,
    ) -> Dict[str, Any]:
        body = {
            _DATA_KEY: {
                "attributes": {
                    "offers": [
                        {
                            "offerAggregateId": offer_aggregate_id,
                            "offerIds": offer_ids,
                            "passengers": [
                                dataclasses.asdict(
                                    passenger,
                                    dict_factory=models.dict_factory_to_camel,
                                )
                                for passenger in passengers
                            ],
                        },
                    ],
                    "contactDetails": dataclasses.asdict(
                        contact_details,
                        dict_factory=models.dict_factory_to_camel,
                    ),
                },
                _TYPE_KEY: "orders",
            },
        }
        response = self._client.post(
            "{0}/orders".format(self._api_url),
            headers=dict(self._auth_headers, **self._post_headers),
            json=body,
        )

        response.raise_for_status()

        return response.json()

    def get_order_by_id(self, order_id: str) -> Dict[str, Any]:
        response = self._client.get(
            "{0}/orders/{1}".format(self._api_url, order_id),
            headers=self._auth_headers,
        )

        response.raise_for_status()

        return response.json()

    @property
    def _auth_headers(self) -> Dict[str, str]:
        return {
            "Authorization": "Bearer {0}".format(self._token),
        }
