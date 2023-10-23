import datetime
import uuid
from collections.abc import AsyncIterable, Mapping, Sequence
from typing import Any

from snowfall.project.junction.go.service.places import places
from snowfall.project.junction.go.service.places.v1 import models_pb2
from snowfall.stdlib import string
from snowfall.stdlib.format import protobuf
from snowfall.stdlib.v1 import latlng_pb2

_NAMESPACE = uuid.UUID("105eba69-b787-48ba-9159-6078e0b76e46")

_MAX_DISTANCE_AIRPORT_M = 5000
_MAX_DISTANCE_GENERAL_TRANSPORT_M = 250
_MAX_DISTANCE_BUS_STATION_M = 50


def invalid_coordinates(
    location: Mapping[str, Any],
) -> bool:
    if location["geometry"]["type"] != "Point":
        return True
    lat, lon = location["geometry"]["coordinates"]
    return lat == lon == 0


def validate_name(node: Mapping[str, Any]) -> str | None:
    properties = node.get("properties", {})
    return (
        properties.get("name:en")
        or properties.get("int_name")
        or properties.get("name")
        or properties.get("alt_name")
    )


def resolve_osm_properties(  # noqa: WPS231
    properties: Mapping[str, Any],
) -> Mapping[str, Any]:
    useful_properties = {
        "type": models_pb2.Location.Type.TYPE_UNSPECIFIED,
        "distance": 0,
        "iata": "",
    }

    iata = properties.get("iata")

    if properties.get("railway") == "station":
        useful_properties["type"] = models_pb2.Location.Type.TYPE_RAILWAY_STATION
        useful_properties["distance"] = _MAX_DISTANCE_GENERAL_TRANSPORT_M
    elif properties.get("aeroway") == "aerodrome" and iata and len(iata) == 3:
        useful_properties["iata"] = iata
        useful_properties["type"] = models_pb2.Location.Type.TYPE_AIRPORT
        useful_properties["distance"] = _MAX_DISTANCE_AIRPORT_M
    elif properties.get("amenity") == "bus_station":
        useful_properties["type"] = models_pb2.Location.Type.TYPE_BUS_STATION
        useful_properties["distance"] = _MAX_DISTANCE_BUS_STATION_M
    elif properties.get("amenity") == "ferry_terminal":
        useful_properties["type"] = models_pb2.Location.Type.TYPE_FERRY_PORT
        useful_properties["distance"] = _MAX_DISTANCE_GENERAL_TRANSPORT_M

    return useful_properties


async def node_to_place(  # noqa: WPS231
    locations_repository: places.LocationRepository,
    nodes: Sequence[Mapping[str, Any]],
) -> AsyncIterable[models_pb2.Place]:
    for node in nodes:
        name = validate_name(node)
        if not name or invalid_coordinates(node):
            continue

        properties = resolve_osm_properties(node["properties"])
        types = properties["type"]

        if types != models_pb2.Location.Type.TYPE_UNSPECIFIED:
            locations = [
                loc.id
                async for loc in await locations_repository.find_within_area_by_type(
                    cursor="",
                    longitude=node["geometry"]["coordinates"][0],
                    latitude=node["geometry"]["coordinates"][1],
                    max_distance_meters=properties["distance"],
                    types=types,
                )
            ]

            if not locations:
                continue

            yield models_pb2.Place(
                location=models_pb2.Location(
                    id=string.to_uuid(node["id"], _NAMESPACE),
                    name=name,
                    coordinates=latlng_pb2.LatLng(
                        latitude=float(node["geometry"]["coordinates"][1]),
                        longitude=float(node["geometry"]["coordinates"][0]),
                    ),
                    types=[types],
                    source_ref=node["id"],
                    updated_at=protobuf.datetime_to_protobuf(
                        datetime.datetime.now(tz=datetime.UTC),
                    ),
                ),
                merged_ids=locations,
                place_attributes=models_pb2.PlaceAttributes(
                    iata=properties["iata"],
                ),
            )
