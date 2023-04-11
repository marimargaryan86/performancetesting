import dataclasses
import json
import pkgutil
from typing import Mapping, Sequence

import aiofiles

from snowfall.vendor.direct_ferries.models import route


@dataclasses.dataclass(frozen=True)
class Route(object):
    route_id: str
    origin: str
    destination: str


def _make_route(route_data: Mapping[str, str]) -> Route:
    return Route(
        route_id=route_data["route_id"],
        origin=route_data["origin"],
        destination=route_data["destination"],
    )


def load_routes() -> list[Route]:
    json_content = pkgutil.get_data(
        "snowfall.project.junction.service.providers.direct_ferries.main",
        "routes.json",
    )

    if json_content is None:
        return []  # TODO: throw exception

    routes = json.loads(json_content.decode("utf-8"))

    return [_make_route(route) for route in routes]


class RouteRepository(object):
    def __init__(self) -> None:
        self._routes = {
            "{0}-{1}".format(route.origin, route.destination): route
            for route in load_routes()
        }

    def get_by_origin_destination(self, origin: str, destination: str) -> Route:
        return self._routes["{0}-{1}".format(origin, destination)]


async def make_routes(
    routes: Sequence[route.Route],
    output_path: str | None = None,
) -> None:
    seen_routes = set()
    route_objects = []

    async with aiofiles.open(output_path or "routes.json", "a+") as out_file:
        for route_obj in routes:
            if not route_obj.port_from.code or not route_obj.port_to.code:
                continue

            if route_obj.route_id not in seen_routes:
                route_objects.append(
                    {
                        "route_id": route_obj.route_id,
                        "origin": route_obj.port_from.code,
                        "destination": route_obj.port_to.code,
                    },
                )
                seen_routes.add(route_obj.route_id)

        await out_file.write(json.dumps(route_objects, indent=4))
