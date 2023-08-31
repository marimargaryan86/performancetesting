from snowfall.project.junction.service.routes.v1 import nodes_pb2
from snowfall.stdlib.persistence.mongo import mixins, repository


class NodeRepository(
    mixins.UpsertMixin[nodes_pb2.Node],
    mixins.FindByIdMixin[nodes_pb2.Node],
    repository.ProtoRepository[nodes_pb2.Node],
):
    _proto = nodes_pb2.Node
