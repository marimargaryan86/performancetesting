import asyncio
import datetime
import uuid
from collections.abc import AsyncIterable, Mapping, Sequence
from typing import Any

from pymongo import GEOSPHERE, IndexModel

from snowfall.project.junction.rocket.service.places import constants, handlers
from snowfall.project.junction.rocket.service.places.typing import (
    PlaceIdentifiers,
    ProviderMappings,
    ProviderTypedDict,
)
from snowfall.project.junction.rocket.service.places.v1alpha import models_pb2
from snowfall.service.geodata.v1 import geocoding_pb2, geocoding_pb2_grpc
from snowfall.stdlib import string
from snowfall.stdlib.format import protobuf
from snowfall.stdlib.logging import stdout
from snowfall.stdlib.persistence.mongo import mixins, repository, resultset
from snowfall.stdlib.v1 import latlng_pb2

_RADIUS_TO_MATCH_NODE_WITH_PROVIDER_PLACE = 5000
_RADIUS_TO_MATCH_PLACE_WITH_CITY = 50000
_NAMESPACE = uuid.UUID("f9ec30af-54df-4bd3-8dd9-6c4b51341d6d")

_logger = stdout.get_logger()


class PlaceRepository(
    repository.ProtoRepository[models_pb2.Place],
    mixins.FindByIdMixin[models_pb2.Place],
    mixins.InsertMixin[models_pb2.Place],
):
    _proto = models_pb2.Place
    _indexes = (
        IndexModel([("coordinates", GEOSPHERE)], background=True),
        IndexModel("name", background=True),
    )

    async def find(
        self,
        cursor: str,
        identifiers: Sequence[str] | None = None,
    ) -> resultset.ResultSet[models_pb2.Place]:
        return await self._find_with_cursor(
            cur=cursor,
            filter_=({
                repository.mongo_id_key: {"$in": identifiers} if identifiers else None,
            }),
        )

    async def find_within_radius(
        self,
        cursor: str,
        coordinates: latlng_pb2.LatLng,
        radius: int,
    ) -> resultset.ResultSet[models_pb2.Place]:
        return await self._find_with_cursor(
            cur=cursor,
            filter_={
                "coordinates": {
                    "$nearSphere": {
                        "$geometry": {
                            "type": "Point",
                            "coordinates": [
                                coordinates.longitude,
                                coordinates.latitude,
                            ],
                        },
                        "$maxDistance": radius,
                    },
                },
            },
        )


def validate_name(node: Mapping[str, Any]) -> str | None:
    properties = node.get("properties", {})
    name = (
        properties.get("name:en")
        or properties.get("int_name")
        or properties.get("name")
        or properties.get("alt_name")
    )
    return name if name and name != "" else None


def resolve_osm_properties(  # noqa: WPS231
    node: Mapping[str, Any],
) -> Mapping[str, Any]:
    useful_properties = {
        "type": models_pb2.Type.TYPE_UNSPECIFIED,
        "iata": None,
    }
    properties = node.get("properties")
    if not properties:
        return useful_properties

    iata = properties.get("iata")

    if properties.get("aeroway") == "aerodrome" and iata and len(iata) == 3:
        useful_properties["iata"] = iata
        useful_properties["type"] = models_pb2.Type.TYPE_AIRPORT
    elif properties.get("railway") == "station":
        useful_properties["type"] = models_pb2.Type.TYPE_RAILWAY_STATION
    elif properties.get("amenity") == "ferry_terminal":
        useful_properties["type"] = models_pb2.Type.TYPE_FERRY_PORT

    return useful_properties


def get_provider_places(
    node: Mapping[str, Any],
    vertical_type: models_pb2.Type.ValueType,
    provider_jsons: ProviderTypedDict,
    iata: str | None,
) -> ProviderMappings:
    provider_places_mapped: ProviderMappings = {
        models_pb2.TYPE_RAILWAY_STATION: [],
        models_pb2.TYPE_FERRY_PORT: [],
        models_pb2.TYPE_AIRPORT: [],
    }

    # We assume that if we have an IATA, this counts as an 'Air Provider' place
    if iata:
        provider_places_mapped[models_pb2.TYPE_AIRPORT].append(
            models_pb2.ProviderPlaceId(
                snowfall_provider_id=constants.IATA_ID,
                provider_place_id=iata,
            ),
        )

    # Process other providers
    for provider_type, provider in provider_jsons.items():
        if provider_type != vertical_type:
            continue
        for provider_id, provider_places in provider.items():
            provider_place_mapped_to_node = handlers.place_within_radius(
                target_coords=(
                    float(node["geometry"]["coordinates"][1]),
                    float(node["geometry"]["coordinates"][0]),
                ),
                radius=_RADIUS_TO_MATCH_NODE_WITH_PROVIDER_PLACE,
                provider_places=provider_places,
            )
            if provider_place_mapped_to_node:
                provider_places_mapped[provider_type].append(
                    models_pb2.ProviderPlaceId(
                        snowfall_provider_id=provider_id,
                        provider_place_id=provider_place_mapped_to_node,
                    ),
                )
    return provider_places_mapped


def has_no_provider_places(provider_places: ProviderMappings) -> bool:
    return (
        not provider_places[models_pb2.TYPE_AIRPORT]
        and not provider_places[models_pb2.TYPE_RAILWAY_STATION]
        and not provider_places[models_pb2.TYPE_FERRY_PORT]
    )


async def get_country_code_and_timezone(
    coordinates: latlng_pb2.LatLng,
    geocoding: geocoding_pb2_grpc.GeocodingServiceStub,
) -> tuple[str, str]:
    country_code, time_zone = await asyncio.gather(
        geocoding.CountryCodeLookup(
            geocoding_pb2.CountryCodeLookupRequest(coordinates=coordinates),
        ),
        geocoding.TimeZoneLookup(
            geocoding_pb2.TimeZoneLookupRequest(coordinates=coordinates),
        ),
    )
    return country_code.country_code, time_zone.time_zone.id


async def osm_nodes_to_places(  # noqa: WPS231
    osm_nodes: Sequence[Mapping[str, Any]],
    provider_jsons: ProviderTypedDict,
    geocoding: geocoding_pb2_grpc.GeocodingServiceStub,
    country_codes_to_countries: Mapping[str, str],
) -> AsyncIterable[models_pb2.Place]:
    for node in osm_nodes:
        name = validate_name(node)
        if not name:
            continue

        properties = resolve_osm_properties(node)
        vertical_type = properties["type"]

        if vertical_type != models_pb2.Type.TYPE_UNSPECIFIED:
            provider_places = get_provider_places(
                node=node,
                vertical_type=vertical_type,
                provider_jsons=provider_jsons,
                iata=properties["iata"],
            )
            if has_no_provider_places(provider_places):
                continue

            coordinates = latlng_pb2.LatLng(
                latitude=float(node["geometry"]["coordinates"][1]),
                longitude=float(node["geometry"]["coordinates"][0]),
            )
            country_code, time_zone = await get_country_code_and_timezone(
                coordinates,
                geocoding,
            )

            yield models_pb2.Place(
                id=string.to_uuid(node["id"], _NAMESPACE),
                source_id=node["id"],
                name=name,
                coordinates=coordinates,
                time_zone=time_zone,
                country_code=country_code,
                country_name=country_codes_to_countries[country_code],
                updated_at=protobuf.datetime_to_protobuf(
                    datetime.datetime.now(tz=datetime.UTC),
                ),
                city=None,
                type=vertical_type,
                search_capabilities=models_pb2.ProviderMappings(
                    rail=provider_places[models_pb2.TYPE_RAILWAY_STATION],
                    ferry=provider_places[models_pb2.TYPE_FERRY_PORT],
                    air=provider_places[models_pb2.TYPE_AIRPORT],
                ),
                contains=None,
            )


async def get_places_within_radius(
    coordinates: latlng_pb2.LatLng,
    places_repository: PlaceRepository,
) -> PlaceIdentifiers:
    return [
        models_pb2.PlaceIdentifier(id=place.id, name=place.name, type=place.type)
        async for place in await places_repository.find_within_radius(
            cursor="",
            coordinates=coordinates,
            radius=_RADIUS_TO_MATCH_PLACE_WITH_CITY,
        )
    ]


async def cities_to_places(
    cities: AsyncIterable[Mapping[str, str]],
    places_repository: PlaceRepository,
    geocoding: geocoding_pb2_grpc.GeocodingServiceStub,
    country_codes_to_countries: Mapping[str, str],
) -> AsyncIterable[models_pb2.Place]:
    async for city in cities:
        if not city["name"]:
            continue
        coordinates = latlng_pb2.LatLng(
            latitude=float(city["latitude"]),
            longitude=float(city["longitude"]),
        )
        places_within = await get_places_within_radius(
            coordinates=coordinates,
            places_repository=places_repository,
        )
        if not places_within:
            continue
        country_code, time_zone = await get_country_code_and_timezone(
            coordinates,
            geocoding,
        )
        yield models_pb2.Place(
            id=string.to_uuid(city["id"], _NAMESPACE),
            source_id=city["id"],
            name=city["name"],
            coordinates=coordinates,
            time_zone=time_zone,
            country_code=country_code,
            country_name=country_codes_to_countries[country_code],
            updated_at=protobuf.datetime_to_protobuf(
                datetime.datetime.now(tz=datetime.UTC),
            ),
            city=None,
            type=models_pb2.TYPE_CITY,
            search_capabilities=None,
            contains=places_within,
        )
