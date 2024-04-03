import json
import pkgutil
from collections.abc import Mapping, Sequence
from typing import Any

import aiofiles

from snowfall.vendor.direct_ferries.models import base, passenger, route


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
        "snowfall.project.junction.service.providers.direct_ferries.main",
        "routes.json",
    )

    if json_content is None:
        return []  # TODO(aramh): throw exception

    routes = json.loads(json_content.decode("utf-8"))

    return [_make_route(route) for route in routes]


class RouteRepository:
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


async def make_routes(
    routes: Sequence[route.Route],
    route_passenger_info_mapping: Mapping[int, passenger.RoutePassengerInfoExtended],
    output_path: str | None = None,
) -> None:
    async with aiofiles.open(output_path or "routes.json", "a+") as out_file:
        await out_file.write(
            json.dumps(
                _route_dicts(routes, route_passenger_info_mapping),
                indent=4,
            ),
        )


def _route_dicts(
    routes: Sequence[route.Route],
    route_pax_info_mapping: Mapping[int, passenger.RoutePassengerInfoExtended],
) -> list[dict[str, Any]]:
    seen_routes = set()
    route_objects = []

    for route_obj in routes:
        if not route_obj.port_from.code or not route_obj.port_to.code:
            continue

        r_id = route_obj.route_id

        if r_id not in seen_routes:
            try:
                passenger_info = route_pax_info_mapping[r_id].passenger_info.dict(
                    by_alias=True,
                )
            except KeyError:
                passenger_info = None

            route_objects.append(
                {
                    "route_id": r_id,
                    "origin": route_obj.port_from.code,
                    "destination": route_obj.port_to.code,
                    "passenger_info": passenger_info,
                },
            )
            seen_routes.add(r_id)

    return route_objects
