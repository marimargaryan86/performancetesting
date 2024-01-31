import abc

from snowfall.project.junction.plus.adapter import errors
from snowfall.project.junction.plus.service.notifications.v1 import (
    grpc_pb2 as notifications_grpc_pb2,
)
from snowfall.project.junction.plus.service.notifications.v1 import (
    grpc_pb2_grpc as notifications_pb2_grpc,
)
from snowfall.project.junction.plus.service.notifications.v1 import models_pb2


class Client(abc.ABC):
    @abc.abstractmethod
    async def publish(
        self,
        event: models_pb2.NotificationEvent,
    ) -> None:
        """Publish event to amqp."""


class DictClient(Client):
    async def publish(
        self,
        event: models_pb2.NotificationEvent,
    ) -> None:
        """Publish for test."""


class GrpcClient(Client):
    def __init__(
        self,
        notification_event_publisher: notifications_pb2_grpc.NotificationEventPublisherServiceStub,
        timeout: int = 10,
    ):
        self._notification_event_publisher = notification_event_publisher
        self._timeout = timeout

    async def publish(
        self,
        event: models_pb2.NotificationEvent,
    ) -> None:
        request = notifications_grpc_pb2.PublishNotificationEventRequest(
            event=event,
        )
        response = await errors.handle_grpc_errors(
            self._notification_event_publisher.PublishNotificationEvent(
                request,
                timeout=self._timeout,
            ),
        )

        if not response.is_success:
            raise errors.UnprocessableEntityError()
