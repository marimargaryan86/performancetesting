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
        subscriber_id: str,
    ) -> notifications_models_pb2.Subscriber:
        """Get Subscriber."""


class DictClient(Client):
    def __init__(
        self,
        subscribers: Sequence[notifications_models_pb2.Subscriber],
    ) -> None:
        self._subscribers = {subscriber.id: subscriber for subscriber in subscribers}

    async def get(
        self,
        subscriber_id: str,
    ) -> notifications_models_pb2.Subscriber:
        subscriber = self._subscribers.get(
            subscriber_id,
        )

        if not subscriber:
            raise errors.NotFoundError()

        return subscriber


class GrpcClient(Client):
    def __init__(
        self,
        subscribers: notifications_pb2_grpc.SubscriberServiceStub,
        timeout: int = 10,
    ):
        self._subscribers = subscribers
        self._timeout = timeout

    async def get(
        self,
        subscriber_id: str,
    ) -> notifications_models_pb2.Subscriber:
        request = notifications_grpc_pb2.GetSubscriberRequest(id=subscriber_id)
        response = await errors.handle_grpc_errors(
            self._subscribers.GetSubscriber(
                request,
                timeout=self._timeout,
            ),
        )

        return response.subscriber
