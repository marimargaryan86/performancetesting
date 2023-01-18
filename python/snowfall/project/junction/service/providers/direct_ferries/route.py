import dataclasses
import json
import os
import pkgutil
from typing import Mapping

dir_path = os.path.dirname(os.path.realpath(__file__))


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
