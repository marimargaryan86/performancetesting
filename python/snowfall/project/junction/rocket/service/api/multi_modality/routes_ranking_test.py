import datetime

import pytest

from snowfall.project.junction.rocket.service.api.multi_modality import (
    routes,
    routes_ranking,
)
from snowfall.project.junction.rocket.service.places.v1alpha import (
    models_pb2,
)
from snowfall.project.junction.v1 import segment_type_pb2


@pytest.fixture()
def segment1() -> routes.Segment:
    return routes.Segment.create(
        origin=models_pb2.Place(id="segment1_origin"),
        destination=models_pb2.Place(id="segment1_destination"),
        segment_type=segment_type_pb2.SEGMENT_TYPE_TRAIN,
    )


def test_ranking_one_route(segment1: routes.Segment) -> None:
    route = routes.Route(
        segments=[segment1],
        estimated_travel_time=datetime.timedelta(hours=1),
        estimated_daily_departures=3,
    )
    simple_route_ranking = routes_ranking.SimpleRouteRanking()
    prioritized_routes = simple_route_ranking([route])
    assert len(prioritized_routes) == 1
    assert prioritized_routes[0] == route
