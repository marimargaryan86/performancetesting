import datetime
import uuid
from collections.abc import AsyncIterable, Mapping
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
) -> Mapping[str, models_pb2.Location.Type.ValueType | int]:
    useful_properties = {
        "type": models_pb2.Location.Type.TYPE_UNSPECIFIED,
        "distance": 0,
    }
    railway = properties.get("railway")
    aeroway_type = properties.get("aeroway")
    amenity = properties.get("amenity")
    highway = properties.get("highway")

    if railway == "station":
        useful_properties["type"] = models_pb2.Location.Type.TYPE_RAILWAY_STATION
        useful_properties["distance"] = _MAX_DISTANCE_GENERAL_TRANSPORT_M
    elif aeroway_type == "aerodrome":
        useful_properties["type"] = models_pb2.Location.Type.TYPE_AIRPORT
        useful_properties["distance"] = _MAX_DISTANCE_AIRPORT_M
    elif amenity == "bus_station" or highway == "bus_stop":
        useful_properties["type"] = models_pb2.Location.Type.TYPE_BUS_STATION
        useful_properties["distance"] = _MAX_DISTANCE_BUS_STATION_M
    elif amenity == "ferry_terminal":
        useful_properties["type"] = models_pb2.Location.Type.TYPE_FERRY_PORT
        useful_properties["distance"] = _MAX_DISTANCE_GENERAL_TRANSPORT_M

    return useful_properties


async def node_to_place(  # noqa: WPS231, WPS210
    locations_repository: places.LocationRepository,
    nodes_collection: Any,
) -> AsyncIterable[models_pb2.Place]:
    async for node in nodes_collection.find({}):
        name = validate_name(node)
        if not name:
            continue

        if invalid_coordinates(node):
            continue
        properties = resolve_osm_properties(node["properties"])
        types = properties["type"]
        locations = [
            location.id
            async for location in await locations_repository.find_within_area_by_type(
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
                types=[types],  # type: ignore[list-item]
                source_ref=node["id"],
                updated_at=protobuf.datetime_to_protobuf(
                    datetime.datetime.now(tz=datetime.UTC),
                ),
            ),
            merged_ids=locations,
        )
