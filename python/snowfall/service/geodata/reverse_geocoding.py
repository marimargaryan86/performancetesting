from __future__ import annotations

import dataclasses
from collections.abc import Sequence
from typing import TYPE_CHECKING, NotRequired, TypedDict

from snowfall.service.geodata.v1 import models_pb2
from snowfall.stdlib.v1 import datetime_pb2, latlng_pb2

if TYPE_CHECKING:
    from mypy_boto3_location import client


class LocationSearchParams(TypedDict):
    IndexName: str  # noqa: WPS115
    Text: str  # noqa: WPS115
    BiasPosition: NotRequired[Sequence[float]]  # noqa: WPS115
    FilterBBox: NotRequired[Sequence[float]]  # noqa: WPS115
    FilterCountries: NotRequired[Sequence[str]]  # noqa: WPS115
    Language: NotRequired[str]  # noqa: WPS115
    MaxResults: NotRequired[int]  # noqa: WPS115


@dataclasses.dataclass(frozen=True)
class Coordinates:
    lat: float
    long: float


class ReverseGeocoder:
    def __init__(
        self,
        aws_location_client: client.LocationServiceClient,
    ):
        self._aws_location_client = aws_location_client

    def get_locations(
        self,
        text: str,
        limit: int,
        filter_countries: Sequence[str],
        language: str,
        bias_pos: Coordinates | None = None,
    ) -> Sequence[models_pb2.Location]:
        search_params = LocationSearchParams(
            IndexName="junction2",
            Text=text,
        )
        if limit:
            search_params["MaxResults"] = limit
        if bias_pos is not None:
            search_params["BiasPosition"] = [
                bias_pos.long,
                bias_pos.lat,
            ]
        if filter_countries:
            search_params["FilterCountries"] = filter_countries
        if language:
            search_params["Language"] = language

        search_results = self._aws_location_client.search_place_index_for_text(
            **search_params,
        )["Results"]

        coordinates = []
        for search_result in search_results:
            place = search_result["Place"]
            coordinates.append(
                models_pb2.Location(
                    id=search_result["PlaceId"],
                    name=place["Label"],
                    address_number=place.get("AddressNumber", ""),
                    country=place["Country"],
                    coordinates=latlng_pb2.LatLng(
                        longitude=place["Geometry"]["Point"][0],
                        latitude=place["Geometry"]["Point"][1],
                    ),
                    time_zone=datetime_pb2.TimeZone(id=place["TimeZone"]["Name"]),
                    interpolated=place.get("Interpolated", False),
                    municipality=place.get("Municipality", ""),
                    neighborhood=place.get("Neighborhood", ""),
                    postal_code=place.get("PostalCode", ""),
                    region=place.get("Region", ""),
                    street=place.get("Street", ""),
                    subregion=place.get("SubRegion", ""),
                    unit_number=place.get("UnitNumber", ""),
                    unit_type=place.get("UnitType", ""),
                ),
            )
        return coordinates
