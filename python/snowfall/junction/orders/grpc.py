import grpc

from snowfall.junction.orders.orders import OrderRepository
from snowfall.junction.orders.v1alpha import orders_pb2, orders_pb2_grpc
from snowfall.transport.grpc import Service


class OrderService(
    Service,
    orders_pb2_grpc.OrderServiceServicer,
):
    def __init__(self, orders_searches: OrderRepository, default_page_size: int):
        self._default_page_size = default_page_size
        self._orders_searches = orders_searches

    def get_name(self) -> str:
        return orders_pb2.DESCRIPTOR.services_by_name["OrderService"].full_name

    def register(self, server: grpc.aio.Server) -> None:
        orders_pb2_grpc.add_OrderServiceServicer_to_server(self, server)

    async def GetOrder(  # type: ignore[override] # noqa: N802
        self,
        request: orders_pb2.GetOrderRequest,
        context: grpc.aio.ServicerContext,
    ) -> orders_pb2.GetOrderResponse:
        # TODO: get order search from mongo
        return orders_pb2.GetOrderResponse()

    async def EnqueueOrder(  # type: ignore[override] # noqa: N802
        self,
        request: orders_pb2.EnqueueOrderRequest,
        context: grpc.aio.ServicerContext,
    ) -> orders_pb2.EnqueueOrderResponse:
        # TODO: enqueue order search from queue
        return orders_pb2.EnqueueOrderResponse()
