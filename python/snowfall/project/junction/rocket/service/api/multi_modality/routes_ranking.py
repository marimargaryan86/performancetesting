from collections.abc import Callable, Sequence
from enum import Enum
from functools import cmp_to_key
from typing import TypeAlias

from snowfall.project.junction.rocket.service.api.multi_modality import (
    routes,
)
from snowfall.project.junction.v1 import segment_type_pb2

RouteRanking: TypeAlias = Callable[
    [Sequence[routes.Route]],
    list[routes.Route],
]


class ForceMixed(Enum):
    unforced = 1
    all_types = 2
    # TODO(regis): Could add for example multi-modal forcing only (meaning
    # it will force multimodal trips up, but not one of each).


class SimpleRouteRanking:
    def __init__(self, force_mixed: ForceMixed = ForceMixed.all_types) -> None:
        self._force_mixed = force_mixed

    def __call__(
        self,
        routes_to_prioritize: Sequence[routes.Route],
    ) -> list[routes.Route]:
        return self._prioritize_routes(routes_to_prioritize)

    def _prioritize_routes(
        self,
        routes_to_prioritize: Sequence[routes.Route],
    ) -> list[routes.Route]:
        optimized_routes = sorted(
            routes_to_prioritize,
            key=cmp_to_key(self._is_route_better),
        )

        if self._force_mixed == ForceMixed.all_types:
            return self._move_mixed_routes_up(optimized_routes)
        return optimized_routes

    # This additionally enforces diversity of results
    # by forcing higher in the ordering at least one travel of each type (
    # air-only, rail-only, and multimodal). This is not necessarily optimal but
    # this is a way to showcase the versality of the system (and this also
    # exercises more code pathes). This will most likely be dropped at some point.
    def _move_mixed_routes_up(  # noqa: WPS231
        self,
        optimized_routes: Sequence[routes.Route],
    ) -> list[routes.Route]:
        res = []
        rest = []
        took_air = False
        took_rail = False
        took_multimodal = False
        for route in optimized_routes:
            exists_air = False
            exists_rail = False
            for segment in route.segments:
                if _is_segment_air(segment.type):
                    exists_air = True
                elif _is_segment_train(segment.type):
                    exists_rail = True

            if not took_multimodal and exists_air and exists_rail:
                res.append(route)
                took_multimodal = True
            elif not took_air and exists_air:
                res.append(route)
                took_air = True
            elif not took_rail and exists_rail:
                res.append(route)
                took_rail = True
            else:
                rest.append(route)

        return [*res, *rest]

    # Heuristic using route metadata to estimate which one is a better option for
    # traveling from A to B. It's a comparison function for sorting, so negative
    # value means route1 is smaller (better) than route2.
    def _is_route_better(self, route1: routes.Route, route2: routes.Route) -> int:
        exists_direct = len(route1.segments) == 1 or len(route2.segments) == 1

        connections = len(route1.segments) - len(route2.segments)

        # If there's a direct, it's always better than non-direct, no matter the
        # time.
        if exists_direct and connections != 0:
            return connections

        # If there's no direct, we start to favor the total time over the number
        # of connections. Note that usually the smallest number of connections will
        # be the shortest time, but in case of very long lay-over we might favor
        # one more connection with a lower total time. We use a scoring function that
        # adds a cost for the number of connections, so the more connection the worst it
        # gets (here we penalize by 1 hour segments).

        penalty_cost = 3600
        route1_travel_time_score = (
            route1.estimated_travel_time.seconds + len(route1.segments) * penalty_cost
        )
        route2_travel_time_score = (
            route2.estimated_travel_time.seconds + len(route2.segments) * penalty_cost
        )

        if route1_travel_time_score != route2_travel_time_score:
            return route1_travel_time_score - route2_travel_time_score

        # If still same, we return the one with smallest number of connections.
        if connections != 0:
            return connections

        # Final tiebreaker is the number of departures per day for the route. The
        # more departure, the better (notice the swapping of order compared to other
        # metrics).
        return route2.estimated_daily_departures - route1.estimated_daily_departures


def _is_segment_air(segment_type: segment_type_pb2.SegmentType.ValueType) -> bool:
    return segment_type == segment_type_pb2.SEGMENT_TYPE_FLIGHT


def _is_segment_train(segment_type: segment_type_pb2.SegmentType.ValueType) -> bool:
    return segment_type == segment_type_pb2.SEGMENT_TYPE_TRAIN
