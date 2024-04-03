import dataclasses
from collections.abc import Mapping
from typing import Any

from snowfall.project.junction.v1 import stop_type_pb2


@dataclasses.dataclass(frozen=True)
class Metadata:
    iata: str | None
    icao: str | None


@dataclasses.dataclass(frozen=True)
class Node:
    ref: str
    name: str
    latitude: float
    longitude: float
    node_type: stop_type_pb2.StopType.ValueType
    metadata: Metadata


def _invalid_coordinates(location: Mapping[str, Any]) -> bool:
    if location["geometry"]["type"] != "Point":
        return True

    lat, lon = location["geometry"]["coordinates"]

    return lat == lon == 0


def _parse_name(node: Mapping[str, Any]) -> str | None:
    properties = node.get("properties", {})
    return (
        properties.get("name:en")
        or properties.get("int_name")
        or properties.get("name")
        or properties.get("alt_name")
    )


def _resolve_metadata(node: Mapping[str, Any]) -> Metadata:
    properties = node.get("properties", {})
    return Metadata(
        iata=properties.get("iata"),
        icao=properties.get("icao"),
    )


def _resolve_type(node: Mapping[str, Any]) -> stop_type_pb2.StopType.ValueType:
    properties = node.get("properties", {})

    if properties.get("railway") == "station":
        return stop_type_pb2.StopType.STOP_TYPE_RAILWAY_STATION

    if properties.get("aeroway") == "aerodrome":
        return stop_type_pb2.StopType.STOP_TYPE_AIRPORT

    return stop_type_pb2.StopType.STOP_TYPE_UNSPECIFIED


def _is_unwanted(node: Mapping[str, Any]) -> bool:
    properties = node.get("properties", {})

    return "military" in properties


def resolve_node(node: Mapping[str, Any]) -> Node | None:
    if _is_unwanted(node):
        return None

    name = _parse_name(node)

    if not name or _invalid_coordinates(node):
        return None

    node_type = _resolve_type(node)

    if node_type == stop_type_pb2.StopType.STOP_TYPE_UNSPECIFIED:
        return None

    return Node(
        ref=node["id"],
        name=name,
        latitude=node["geometry"]["coordinates"][1],
        longitude=node["geometry"]["coordinates"][0],
        node_type=node_type,
        metadata=_resolve_metadata(node),
    )
