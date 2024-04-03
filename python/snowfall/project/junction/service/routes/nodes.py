import asyncio
from collections.abc import AsyncGenerator, Iterable, Mapping, Sequence
from typing import Any

import more_itertools

from snowfall.project.junction.service.routes import osm, repositories
from snowfall.project.junction.service.routes.v1 import nodes_pb2
from snowfall.service.geodata.v1 import geocoding_pb2, geocoding_pb2_grpc
from snowfall.stdlib import string
from snowfall.stdlib.logging import stdout
from snowfall.stdlib.v1 import latlng_pb2


class NodeImporter:
    def __init__(
        self,
        geodata: geocoding_pb2_grpc.GeocodingServiceStub,
        repository: repositories.NodeRepository,
        concurrency: int = 100,
    ):
        self._geodata = geodata
        self._repository = repository
        self._concurrency = concurrency
        self._logger = stdout.get_logger()

    async def import_nodes(self, nodes: Sequence[Mapping[str, Any]]) -> None:
        filtered_nodes = filter(None, [osm.resolve_node(node) for node in nodes])

        async for resolved_nodes in self._resolve_nodes(filtered_nodes):
            await asyncio.gather(
                *[self._repository.upsert(node) for node in resolved_nodes],
            )

    async def _resolve_nodes(
        self,
        nodes: Iterable[osm.Node],
    ) -> AsyncGenerator[list[nodes_pb2.Node], None]:
        for chunk in more_itertools.ichunked(nodes, self._concurrency):
            yield await asyncio.gather(
                *[self._node_to_proto(node) for node in chunk],
            )

    async def _node_to_proto(self, node: osm.Node) -> nodes_pb2.Node:
        coordinates = latlng_pb2.LatLng(
            latitude=node.latitude,
            longitude=node.longitude,
        )
        (timezone_response, country_code_response) = await asyncio.gather(
            self._geodata.TimeZoneLookup(
                geocoding_pb2.TimeZoneLookupRequest(coordinates=coordinates),
            ),
            self._geodata.CountryCodeLookup(
                geocoding_pb2.CountryCodeLookupRequest(coordinates=coordinates),
            ),
        )

        return nodes_pb2.Node(
            id=string.to_uuid(node.ref),
            osm_ref=node.ref,
            name=node.name,
            coordinates=coordinates,
            time_zone=timezone_response.time_zone,
            country_code=country_code_response.country_code,
            type=node.node_type,
            metadata=nodes_pb2.Node.Metadata(
                iata=node.metadata.iata or "",
                icao=node.metadata.icao or "",
            ),
        )
