from grpc import StatusCode, aio

from snowfall.project.junction.plus.service.notifications.notifications import (
    ConfigurationVectorRepository,
    MonitoringRuleRepository,
    OrderRepository,
    SubscriberRepository,
)
from snowfall.project.junction.plus.service.notifications.v1alpha import (
    grpc_pb2 as notifications_pb2,
)
from snowfall.project.junction.plus.service.notifications.v1alpha import (
    grpc_pb2_grpc as notifications_pb2_grpc,
)
from snowfall.stdlib.transport.amqp import producer
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


class MonitoringRuleService(
    service.Service,
    notifications_pb2_grpc.MonitoringRuleServiceServicer,
):
    def __init__(
        self,
        monitoring_rules: MonitoringRuleRepository,
    ):
        self._monitoring_rules = monitoring_rules

    def get_name(self) -> str:
        return notifications_pb2.DESCRIPTOR.services_by_name[
            "MonitoringRuleService"
        ].full_name

    def register(self, server: aio.Server) -> None:
        notifications_pb2_grpc.add_MonitoringRuleServiceServicer_to_server(
            self,
            server,
        )

    async def GetMonitoringRule(  # type: ignore[override] # noqa: N802
        self,
        request: notifications_pb2.GetMonitoringRuleRequest,
        context: aio.ServicerContext,
    ) -> notifications_pb2.GetMonitoringRuleResponse:
        monitoring_rule = await self._monitoring_rules.find_by_id(
            request.monitoring_rule_id,
        )
        if monitoring_rule is None:
            await context.abort(StatusCode.NOT_FOUND)

        return notifications_pb2.GetMonitoringRuleResponse(
            monitoring_rule=monitoring_rule,
        )

    async def GetMonitoringRuleByBooking(  # type: ignore[override] # noqa: N802
        self,
        request: notifications_pb2.GetMonitoringRuleByBookingRequest,
        context: aio.ServicerContext,
    ) -> notifications_pb2.GetMonitoringRuleByBookingResponse:
        monitoring_rule = await self._monitoring_rules.find_by_booking(request.booking)
        if not monitoring_rule:
            await context.abort(StatusCode.NOT_FOUND)
        return notifications_pb2.GetMonitoringRuleByBookingResponse(
            monitoring_rule=monitoring_rule,
        )

    async def CreateMonitoringRule(  # type: ignore[override] # noqa: N802
        self,
        request: notifications_pb2.CreateMonitoringRuleRequest,
        context: aio.ServicerContext,
    ) -> notifications_pb2.CreateMonitoringRuleResponse:
        await self._monitoring_rules.insert(request.monitoring_rule)
        return notifications_pb2.CreateMonitoringRuleResponse(
            monitoring_rule=request.monitoring_rule,
        )

    async def UpdateMonitoringRule(  # type: ignore[override] # noqa: N802
        self,
        request: notifications_pb2.UpdateMonitoringRuleRequest,
        context: aio.ServicerContext,
    ) -> notifications_pb2.UpdateMonitoringRuleResponse:
        update_status = await self._monitoring_rules.upsert(request.monitoring_rule)
        return notifications_pb2.UpdateMonitoringRuleResponse(
            is_success=update_status,
        )


class NotificationEventPublisherService(
    service.Service,
    notifications_pb2_grpc.NotificationEventPublisherServiceServicer,
):
    def __init__(
        self,
        producer_obj: producer.Producer,
    ):
        self._producer = producer_obj

    def get_name(self) -> str:
        return notifications_pb2.DESCRIPTOR.services_by_name[
            "NotificationEventPublisherService"
        ].full_name

    def register(self, server: aio.Server) -> None:
        notifications_pb2_grpc.add_NotificationEventPublisherServiceServicer_to_server(
            self,
            server,
        )

    async def PublishNotificationEvent(  # type: ignore[override] # noqa: N802
        self,
        request: notifications_pb2.PublishNotificationEventRequest,
        context: aio.ServicerContext,
    ) -> notifications_pb2.PublishNotificationEventResponse:
        await self._producer.publish(request.event, "plus.events")
        return notifications_pb2.PublishNotificationEventResponse(
            is_success=True,
        )
