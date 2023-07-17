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


class Client(abc.ABC):
    @abc.abstractmethod
    async def get(
        self,
        booking: notifications_models_pb2.Booking,
    ) -> notifications_models_pb2.MonitoringRule:
        """Get Monitoring Rule."""

    @abc.abstractmethod
    async def create(
        self,
        monitoring_rule: notifications_models_pb2.MonitoringRule,
    ) -> notifications_models_pb2.MonitoringRule:
        """Create Monitoring Rule."""

    @abc.abstractmethod
    async def update(
        self,
        monitoring_rule: notifications_models_pb2.MonitoringRule,
    ) -> None:
        """Update Monitoring Rule."""


class DictClient(Client):
    def __init__(
        self,
        monitoring_rules: Sequence[notifications_models_pb2.MonitoringRule],
    ) -> None:
        self._monitoring_rules = {
            monitoring_rule.booking.value.id: monitoring_rule
            for monitoring_rule in monitoring_rules
        }

    async def get(
        self,
        booking: notifications_models_pb2.Booking,
    ) -> notifications_models_pb2.MonitoringRule:
        monitoring_rule = self._monitoring_rules.get(
            booking.value.id,
        )

        if not monitoring_rule:
            raise errors.NotFoundError()

        return monitoring_rule

    async def create(
        self,
        monitoring_rule: notifications_models_pb2.MonitoringRule,
    ) -> notifications_models_pb2.MonitoringRule:
        self._monitoring_rules[monitoring_rule.booking.value.id] = monitoring_rule
        return monitoring_rule

    async def update(
        self,
        monitoring_rule: notifications_models_pb2.MonitoringRule,
    ) -> None:
        self._monitoring_rules[monitoring_rule.booking.value.id] = monitoring_rule


class GrpcClient(Client):
    def __init__(
        self,
        monitoring_rules: notifications_pb2_grpc.MonitoringRuleServiceStub,
        timeout: int = 10,
    ):
        self._monitoring_rules = monitoring_rules
        self._timeout = timeout

    async def get(
        self,
        booking: notifications_models_pb2.Booking,
    ) -> notifications_models_pb2.MonitoringRule:
        request = notifications_grpc_pb2.GetMonitoringRuleRequest(booking=booking)
        response = await errors.handle_grpc_errors(
            self._monitoring_rules.GetMonitoringRule(
                request,
                timeout=self._timeout,
            ),
        )

        return response.monitoring_rule

    async def create(
        self,
        monitoring_rule: notifications_models_pb2.MonitoringRule,
    ) -> notifications_models_pb2.MonitoringRule:
        request = notifications_grpc_pb2.CreateMonitoringRuleRequest(
            monitoring_rule=monitoring_rule,
        )
        response = await errors.handle_grpc_errors(
            self._monitoring_rules.CreateMonitoringRule(
                request,
                timeout=self._timeout,
            ),
        )

        return response.monitoring_rule

    async def update(
        self,
        monitoring_rule: notifications_models_pb2.MonitoringRule,
    ) -> None:
        request = notifications_grpc_pb2.UpdateMonitoringRuleRequest(
            monitoring_rule=monitoring_rule,
        )
        response = await errors.handle_grpc_errors(
            self._monitoring_rules.UpdateMonitoringRule(
                request,
                timeout=self._timeout,
            ),
        )

        if not response.is_success:
            raise errors.UnprocessableEntityError()
