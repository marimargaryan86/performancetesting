import datetime
from typing import Any

import lagom
from grpc import aio

from snowfall.project.junction.rocket.service.api.air import (
    repositories,
    types,
)
from snowfall.project.junction.rocket.service.api.air.transforms import (
    transforms as air_transforms,
)
from snowfall.project.junction.rocket.service.searches.v1alpha import grpc_pb2_grpc
from snowfall.vendor.junction_one.client import JunctionOneClient


def create_dependencies(
    *,
    grpc_timeout: datetime.timedelta,
    searches_channel: aio.Channel,
    junction_one_client: JunctionOneClient,
    mongo: Any,
) -> lagom.Container:
    container = lagom.Container()

    container[datetime.timedelta] = grpc_timeout
    container[grpc_pb2_grpc.SearchServiceStub] = grpc_pb2_grpc.SearchServiceStub(
        searches_channel,
    )
    container[grpc_pb2_grpc.SearchResultServiceStub] = (
        grpc_pb2_grpc.SearchResultServiceStub(searches_channel)
    )
    container[JunctionOneClient] = junction_one_client
    container[types.AbstractAirSearchRepo] = repositories.AirSearchRepo(  # type: ignore[type-abstract]
        collection=mongo.searches.air_results,
    )
    container[types.AirSearchRequestTransformer] = (  # type: ignore[type-abstract]
        air_transforms.AirSearchRequestTransformer
    )
    container[types.AirSearchResultTransformer] = (  # type: ignore[type-abstract]
        air_transforms.AirSearchResultTransformer
    )

    return container
