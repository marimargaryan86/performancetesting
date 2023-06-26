from grpc import aio

from snowfall.project.junction.plus.service.notifications.notifications import (
    OrderRepository,
    SubscriberRepository,
)
from snowfall.project.junction.plus.service.notifications.v1alpha import (
    grpc_pb2 as notifications_pb2,
)
from snowfall.project.junction.plus.service.notifications.v1alpha import (
    grpc_pb2_grpc as notifications_pb2_grpc,
)
from snowfall.stdlib.transport.grpc import service


class OrderService(
    service.Service,
    notifications_pb2_grpc.OrderServiceServicer,
):
    def __init__(
        self,
        orders: OrderRepository,
        subscribers: SubscriberRepository,
    ):
        self._orders = orders
        self._subscribers = subscribers

    def get_name(self) -> str:
        return notifications_pb2.DESCRIPTOR.services_by_name["OrderService"].full_name

    def register(self, server: aio.Server) -> None:
        notifications_pb2_grpc.add_OrderServiceServicer_to_server(self, server)

    async def CreateOrder(  # type: ignore[override] # noqa: N802
        self,
        request: notifications_pb2.CreateOrderRequest,
        context: aio.ServicerContext,
    ) -> notifications_pb2.CreateOrderResponse:
        subscriber = await self._subscribers.get_or_create(
            request.reseller_id,
            request.contact_details,
        )
        order = await self._orders.create(
            request.reseller_id,
            request.external_ref_id,
            request.passengers,
            request.bookings,
            subscriber,
        )

        return notifications_pb2.CreateOrderResponse(order=order)
