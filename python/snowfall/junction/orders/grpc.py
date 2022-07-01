from grpc import StatusCode, aio

from snowfall.junction.orders.amqp import OrderProducer
from snowfall.junction.orders.orders import OrderRepository
from snowfall.junction.orders.v1alpha import orders_pb2, orders_pb2_grpc
from snowfall.stdlib.transport.grpc import service


class OrderService(
    service.Service,
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

    def register(self, server: aio.Server) -> None:
        orders_pb2_grpc.add_OrderServiceServicer_to_server(self, server)

    async def GetOrder(  # type: ignore[override] # noqa: N802
        self,
        request: orders_pb2.GetOrderRequest,
        context: aio.ServicerContext,
    ) -> orders_pb2.GetOrderResponse:
        order = await self._orders.find_by_id(request.id)

        if order is None:
            await context.abort(StatusCode.NOT_FOUND)

        return orders_pb2.GetOrderResponse(order=order)

    async def AddOffersToOrder(  # type: ignore[override] # noqa: N802
        self,
        request: orders_pb2.AddOffersToOrderRequest,
        context: aio.ServicerContext,
    ) -> orders_pb2.AddOffersToOrderResponse:
        order = await self._orders.amend_order(
            order_id=request.order_id,
            offer_ids=request.offer_ids,
        )

        # TODO: maybe it would be better to publish offers instead of orders
        # because some orders might have already been booked at this point
        await self._publisher.publish(order)

        return orders_pb2.AddOffersToOrderResponse(order=order)

    async def EnqueueOrder(  # type: ignore[override] # noqa: N802
        self,
        request: orders_pb2.EnqueueOrderRequest,
        context: aio.ServicerContext,
    ) -> orders_pb2.EnqueueOrderResponse:
        order = await self._orders.create_from_offers(
            offer_ids=request.offer_ids,
            contact_details=request.contact_details,
            passengers=request.passengers,
        )

        await self._publisher.publish(order)

        return orders_pb2.EnqueueOrderResponse(order=order)

    async def ListOrders(  # type: ignore[override] # noqa: N802
        self,
        request: orders_pb2.ListOrdersRequest,
        context: aio.ServicerContext,
    ) -> orders_pb2.ListOrdersResponse:
        orders_result = await self._orders.find(request.page_token)

        orders_result.limit(
            request.page_size if request.page_size else self._default_page_size,
        )

        return orders_pb2.ListOrdersResponse(
            orders=[order async for order in orders_result],
            next_page_token=await orders_result.cursor(),
        )
