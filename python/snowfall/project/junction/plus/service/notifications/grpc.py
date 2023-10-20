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

    async def GetOrder(  # type: ignore[override] # noqa: N802
        self,
        request: notifications_pb2.GetOrderRequest,
        context: aio.ServicerContext,
    ) -> notifications_pb2.GetOrderResponse:
        order = await self._orders.find_by_id(request.id)

        if order is None:
            return await context.abort(StatusCode.NOT_FOUND)

        return notifications_pb2.GetOrderResponse(
            order=order,
        )

    async def FindOrders(  # type: ignore[override] # noqa: N802
        self,
        request: notifications_pb2.FindOrdersRequest,
        context: aio.ServicerContext,
    ) -> notifications_pb2.FindOrdersResponse:
        orders = [
            order
            async for order in await self._orders.find(
                request.identifier,
                request.selector,
            )
        ]

        return notifications_pb2.FindOrdersResponse(
            orders=orders,
        )


class SubscriberService(  # noqa: WPS214
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
            return await context.abort(StatusCode.NOT_FOUND)

        return notifications_pb2.GetSubscriberResponse(
            subscriber=subscriber,
        )

    async def GetSubscriberFromReseller(  # type: ignore[override] # noqa: N802
        self,
        request: notifications_pb2.GetSubscriberFromResellerRequest,
        context: aio.ServicerContext,
    ) -> notifications_pb2.GetSubscriberResponse:
        subscriber = await self._subscribers.find_by_reseller(
            request.reseller_id,
            request.mobile_phone,
        )

        if subscriber is None:
            return await context.abort(StatusCode.NOT_FOUND)

        return notifications_pb2.GetSubscriberResponse(
            subscriber=subscriber,
        )

    async def Unsubscribe(  # type: ignore[override]  # noqa: N802
        self,
        request: notifications_pb2.UnsubscribeRequest,
        context: aio.ServicerContext,
    ) -> notifications_pb2.UnsubscribeResponse:
        unsubscribe_status = await self._subscribers.unsubscribe(request.identifier)
        return notifications_pb2.UnsubscribeResponse(
            is_success=unsubscribe_status,
        )

    async def Subscribe(  # type: ignore[override]  # noqa: N802
        self,
        request: notifications_pb2.SubscribeRequest,
        context: aio.ServicerContext,
    ) -> notifications_pb2.SubscribeResponse:
        subscribe_status = await self._subscribers.subscribe(request.identifier)
        return notifications_pb2.SubscribeResponse(
            is_success=subscribe_status,
        )

    async def UpdatePushNotificationToken(  # type: ignore[override]  # noqa: N802
        self,
        request: notifications_pb2.UpdatePushNotificationTokenRequest,
        context: aio.ServicerContext,
    ) -> notifications_pb2.UpdatePushNotificationTokenResponse:
        update_status = await self._subscribers.update_push_notifications_token(
            request.reseller_id,
            request.mobile_phone,
            request.push_notification_token,
        )
        return notifications_pb2.UpdatePushNotificationTokenResponse(
            is_success=update_status,
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
        configuration_vector = await self._configuration_vectors.find_by_selector(
            selection_value=request.identifier,
            selector=request.selector,
        )

        if configuration_vector is None:
            return await context.abort(StatusCode.NOT_FOUND)

        return notifications_pb2.GetConfigurationVectorResponse(
            configuration_vector=configuration_vector,
        )

    async def CreateConfigurationVector(  # type: ignore[override] # noqa: N802
        self,
        request: notifications_pb2.CreateConfigurationVectorRequest,
        context: aio.ServicerContext,
    ) -> notifications_pb2.CreateConfigurationVectorResponse:
        await self._configuration_vectors.insert(request.configuration_vector)
        return notifications_pb2.CreateConfigurationVectorResponse(
            configuration_vector=request.configuration_vector,
        )

    async def UpdateConfigurationVector(  # type: ignore[override] # noqa: N802
        self,
        request: notifications_pb2.UpdateConfigurationVectorRequest,
        context: aio.ServicerContext,
    ) -> notifications_pb2.UpdateConfigurationVectorResponse:
        update_status = await self._configuration_vectors.update(
            request.configuration_vector,
        )
        return notifications_pb2.UpdateConfigurationVectorResponse(
            is_success=update_status,
        )


class MonitoringRuleService(  # noqa: WPS214
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
            return await context.abort(StatusCode.NOT_FOUND)

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
            return await context.abort(StatusCode.NOT_FOUND)
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

    async def FindMonitoringRules(  # type: ignore[override] # noqa: N802
        self,
        request: notifications_pb2.FindMonitoringRulesRequest,
        context: aio.ServicerContext,
    ) -> notifications_pb2.FindMonitoringRulesResponse:
        monitoring_rules = [
            monitoring_rule
            async for monitoring_rule in await self._monitoring_rules.find_rules_for_upcoming_events(
                request.departure_after,
                request.sent_flag,
            )
        ]
        return notifications_pb2.FindMonitoringRulesResponse(
            monitoring_rules=monitoring_rules,
        )

    async def UpdateCheckinReminder(  # type: ignore[override] # noqa: N802
        self,
        request: notifications_pb2.UpdateCheckinReminderRequest,
        context: aio.ServicerContext,
    ) -> notifications_pb2.UpdateCheckinReminderResponse:
        update_status = await self._monitoring_rules.update_checkin_reminder(
            request.identifier,
        )
        return notifications_pb2.UpdateCheckinReminderResponse(
            is_success=update_status,
        )

    async def UpdateWeatherReport(  # type: ignore[override] # noqa: N802
        self,
        request: notifications_pb2.UpdateWeatherReportRequest,
        context: aio.ServicerContext,
    ) -> notifications_pb2.UpdateWeatherReportResponse:
        update_status = await self._monitoring_rules.update_weather_report(
            request.identifier,
        )
        return notifications_pb2.UpdateWeatherReportResponse(
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
