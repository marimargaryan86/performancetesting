import grpc

from snowfall.junction.orders.amqp import OrderProducer
from snowfall.junction.orders.orders import OrderRepository
from snowfall.junction.orders.v1alpha import orders_pb2, orders_pb2_grpc
from snowfall.stdlib.transport.grpc import Service


class OrderService(
    Service,
    orders_pb2_grpc.OrderServiceServicer,
):
    def __init__(
        self,
        orders: OrderRepository,
        publisher: OrderProducer,
        default_page_size: int,
    ):
        self._default_page_size = default_page_size
        self._orders = orders
        self._publisher = publisher

    def get_name(self) -> str:
        return orders_pb2.DESCRIPTOR.services_by_name["OrderService"].full_name

    def register(self, server: grpc.aio.Server) -> None:
        orders_pb2_grpc.add_OrderServiceServicer_to_server(self, server)

    async def GetOrder(  # type: ignore[override] # noqa: N802
        self,
        request: orders_pb2.GetOrderRequest,
        context: grpc.aio.ServicerContext,
    ) -> orders_pb2.GetOrderResponse:
        order = await self._orders.find_by_id(request.id)

        if not order:
            await context.abort(grpc.StatusCode.NOT_FOUND)

        return orders_pb2.GetOrderResponse(order=order)

    async def EnqueueOrder(  # type: ignore[override] # noqa: N802
        self,
        request: orders_pb2.EnqueueOrderRequest,
        context: grpc.aio.ServicerContext,
    ) -> orders_pb2.EnqueueOrderResponse:
        order = await self._orders.create(
            request.offers,
        )

        await self._publisher.publish(order)

        return orders_pb2.EnqueueOrderResponse(order=order)
