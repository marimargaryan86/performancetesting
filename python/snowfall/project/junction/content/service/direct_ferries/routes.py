import json
import pkgutil
from collections.abc import Mapping
from typing import Any

from snowfall.vendor.direct_ferries.models import base, passenger


class Route(base.CamelCaseBaseModel):
    route_id: int
    origin: str
    destination: str
    passenger_info: passenger.RoutePassengerInfo | None = None


def _make_route(route_data: Mapping[str, Any]) -> Route:
    try:
        passenger_info = passenger.RoutePassengerInfo(
            **route_data["passenger_info"],
        )
    except KeyError:
        passenger_info = None

    return Route(
        route_id=route_data["route_id"],
        origin=route_data["origin"],
        destination=route_data["destination"],
        passenger_info=passenger_info,
    )


def load_routes() -> list[Route]:
    json_content = pkgutil.get_data(
        "snowfall.project.junction.content.service.direct_ferries.routes",
        "routes.json",
    )

    if json_content is None:
        raise RuntimeError("routes.json not found")

    routes = json.loads(json_content.decode("utf-8"))

    return [_make_route(route) for route in routes]


class RouteRepository(object):
    def __init__(self) -> None:
        route_objects = load_routes()

        self._routes_per_ond = {
            "{0}-{1}".format(route.origin, route.destination): route
            for route in route_objects
        }
        self._routes_per_id = {route.route_id: route for route in route_objects}

    def get_by_origin_destination(self, origin: str, destination: str) -> Route:
        return self._routes_per_ond["{0}-{1}".format(origin, destination)]

    def get_by_id(self, route_id: int) -> Route:
        return self._routes_per_id[route_id]
