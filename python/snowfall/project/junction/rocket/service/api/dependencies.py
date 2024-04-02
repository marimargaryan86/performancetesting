import datetime

import lagom

from snowfall.project.junction.rocket.service.searches.v1alpha import grpc_pb2_grpc


def create_dependencies(
    grpc_timeout: datetime.timedelta,
    searches: grpc_pb2_grpc.SearchServiceStub,
    search_results: grpc_pb2_grpc.SearchResultServiceStub,
) -> lagom.Container:
    container = lagom.Container()

    container[datetime.timedelta] = grpc_timeout
    container[grpc_pb2_grpc.SearchServiceStub] = searches
    container[grpc_pb2_grpc.SearchResultServiceStub] = search_results

    return container
