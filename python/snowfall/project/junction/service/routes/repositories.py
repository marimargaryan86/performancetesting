from snowfall.project.junction.service.routes.v1 import nodes_pb2, stops_pb2
from snowfall.stdlib.persistence.mongo import mixins, repository


class NodeRepository(
    repository.ProtoRepository[nodes_pb2.Node],
    mixins.UpsertMixin[nodes_pb2.Node],
    mixins.FindByIdMixin[nodes_pb2.Node],
):
    _proto = nodes_pb2.Node


class StopRepository(
    repository.ProtoRepository[stops_pb2.Stop],
    mixins.UpsertMixin[stops_pb2.Stop],
    mixins.FindByIdMixin[stops_pb2.Stop],
):
    _proto = stops_pb2.Stop
