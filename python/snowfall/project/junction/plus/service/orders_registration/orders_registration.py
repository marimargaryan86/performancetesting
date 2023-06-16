from snowfall.project.junction.plus.service.orders_registration.v1alpha import (
    models_pb2,
)
from snowfall.stdlib.persistence.mongo import repository


class OrderRepository(repository.ProtoRepository[models_pb2.Order]):
    _proto = models_pb2.Order
