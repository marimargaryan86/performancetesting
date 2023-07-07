from grpc import StatusCode, aio

from snowfall.project.junction.plus.service.notifications.notifications import (
    ConfigurationVectorRepository,
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
            request.passengers[0],
        )
        order = await self._orders.create(
            request.reseller_id,
            request.external_ref_id,
            request.booking_reference,
            request.passengers,
            request.bookings,
            subscriber,
        )

        return notifications_pb2.CreateOrderResponse(order=order)


class SubscriberService(
    service.Service,
    notifications_pb2_grpc.SubscriberServiceServicer,
):
    def __init__(
        self,
        subscribers: SubscriberRepository,
    ):
        self._subscribers = subscribers

    def get_name(self) -> str:
        return notifications_pb2.DESCRIPTOR.services_by_name[
            "SubscriberService"
        ].full_name

    def register(self, server: aio.Server) -> None:
        notifications_pb2_grpc.add_SubscriberServiceServicer_to_server(self, server)

    async def GetSubscriber(  # type: ignore[override] # noqa: N802
        self,
        request: notifications_pb2.GetSubscriberRequest,
        context: aio.ServicerContext,
    ) -> notifications_pb2.GetSubscriberResponse:
        subscriber = await self._subscribers.find_by_id(request.id)

        if subscriber is None:
            await context.abort(StatusCode.NOT_FOUND)

        return notifications_pb2.GetSubscriberResponse(
            subscriber=subscriber,
        )


class ConfigurationVectorService(
    service.Service,
    notifications_pb2_grpc.ConfigurationVectorServiceServicer,
):
    def __init__(
        self,
        configuration_vectors: ConfigurationVectorRepository,
    ):
        self._configuration_vectors = configuration_vectors

    def get_name(self) -> str:
        return notifications_pb2.DESCRIPTOR.services_by_name[
            "ConfigurationVectorService"
        ].full_name

    def register(self, server: aio.Server) -> None:
        notifications_pb2_grpc.add_ConfigurationVectorServiceServicer_to_server(
            self,
            server,
        )

    async def GetConfigurationVector(  # type: ignore[override] # noqa: N802
        self,
        request: notifications_pb2.GetConfigurationVectorRequest,
        context: aio.ServicerContext,
    ) -> notifications_pb2.GetConfigurationVectorResponse:
        configuration_vector = await self._configuration_vectors.find_by_id(
            request.reseller_id,
            "reseller_id",
        )

        if configuration_vector is None:
            await context.abort(StatusCode.NOT_FOUND)

        return notifications_pb2.GetConfigurationVectorResponse(
            configuration_vector=configuration_vector,
        )
