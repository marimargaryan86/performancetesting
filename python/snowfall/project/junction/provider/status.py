import datetime

from snowfall.stdlib.persistence.redis import types
from snowfall.stdlib.transport.amqp import trackable
from snowfall.stdlib.v1 import amqp_pb2

_SUBTASK_TIMEOUT_MINUTES = 15


class SubtaskStatusHandler(trackable.FixedSizeStatusHandler):
    """Usable when splitting a search task up into several subtasks internally."""

    def __init__(
        self,
        reporter: trackable.StatusReporter,
        redis: types.Client[str],
        trackable_key: str,
    ) -> None:
        super().__init__(redis)

        self._reporter = reporter
        self._trackable_key = trackable_key

    async def set_expected_size(
        self,
        trackable_id: str,
        num_of_tasks: int,
    ) -> None:
        await super().set_expected_size(trackable_id, num_of_tasks)
        await self._on_processing(amqp_pb2.Trackable(id=trackable_id))

        if not num_of_tasks:
            await self._on_completed(amqp_pb2.Trackable(id=trackable_id))

    async def _get_status_and_expiry_by_id(
        self,
        trackable_id: str,
    ) -> tuple[amqp_pb2.Trackable.Status.ValueType, datetime.datetime]:
        return (
            amqp_pb2.Trackable.Status.STATUS_PROCESSING,
            datetime.datetime.now(tz=datetime.timezone.utc)
            + datetime.timedelta(
                minutes=_SUBTASK_TIMEOUT_MINUTES,
            ),
        )

    async def _on_completed(self, msg: amqp_pb2.Trackable) -> None:
        await self._reporter.ack(
            {
                trackable.TRACKABLE_ID: msg.id,
                trackable.TRACKABLE_ROUTING_KEY: self._trackable_key,
            },
        )

    async def _on_failed(self, msg: amqp_pb2.Trackable) -> None:
        await self._reporter.nack(
            {
                trackable.TRACKABLE_ID: msg.id,
                trackable.TRACKABLE_ROUTING_KEY: self._trackable_key,
            },
        )

    async def _on_processing(self, msg: amqp_pb2.Trackable) -> None:
        await self._reporter.receive(
            {
                trackable.TRACKABLE_ID: msg.id,
                trackable.TRACKABLE_ROUTING_KEY: self._trackable_key,
            },
        )
