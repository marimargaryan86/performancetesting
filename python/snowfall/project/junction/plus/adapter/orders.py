import abc
from collections.abc import Sequence

from snowfall.project.junction.plus.adapter import errors
from snowfall.project.junction.plus.service.notifications.v1alpha import (
    grpc_pb2 as notifications_grpc_pb2,
)
from snowfall.project.junction.plus.service.notifications.v1alpha import (
    grpc_pb2_grpc as notifications_pb2_grpc,
)
from snowfall.project.junction.plus.service.notifications.v1alpha import (
    models_pb2 as notifications_models_pb2,
)
from snowfall.stdlib import string


class Client(abc.ABC):
    @abc.abstractmethod
    async def create(
        self,
        create_order_request: notifications_grpc_pb2.CreateOrderRequest,
    ) -> notifications_models_pb2.PersistedOrder:
        """Persist an incoming order from orders registration queue."""


class DictClient(Client):
    def __init__(self, orders: Sequence[notifications_models_pb2.PersistedOrder]):
        self._orders = {order.id: order for order in orders}

    async def create(
        self,
        create_order_request: notifications_grpc_pb2.CreateOrderRequest,
    ) -> notifications_models_pb2.PersistedOrder:
        new_order = notifications_models_pb2.PersistedOrder(
            id=string.uuid(),
            reseller_id=create_order_request.reseller_id,
            external_ref_id=create_order_request.external_ref_id,
            subscriber_id=string.uuid(),
            passengers=create_order_request.passengers,
            bookings=create_order_request.bookings,
        )
        self._orders[new_order.id] = new_order
        return new_order


class GrpcClient(Client):
    def __init__(
        self,
        orders: notifications_pb2_grpc.OrderServiceStub,
        timeout: int = 10,
    ):
        self._orders = orders
        self._timeout = timeout

    async def create(
        self,
        create_order_request: notifications_grpc_pb2.CreateOrderRequest,
    ) -> notifications_models_pb2.PersistedOrder:
        response = await errors.handle_grpc_errors(
            self._orders.CreateOrder(
                create_order_request,
                timeout=self._timeout,
            ),
        )

        return response.order
