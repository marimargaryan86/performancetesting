from nio import AsyncClient, Event, MatrixRoom

from snowfall.project.junction.plus.adapter import configuration_vectors, subscribers
from snowfall.stdlib.logging import stdout
from snowfall.stdlib.persistence.redis import types as redis


class MatrixCallbacks(object):
    def __init__(
        self,
        matrix_client: AsyncClient,
        redis_client: redis.Client[str],
        subscribers_client: subscribers.Client,
        configuration_vectors_client: configuration_vectors.Client,
    ):
        self._client = matrix_client
        self._redis = redis_client
        self._subscribers = subscribers_client
        self._configuration_vectors = configuration_vectors_client
        self._logger = stdout.get_logger()

    async def message_callback(
        self,
        room: MatrixRoom,
        event: Event,
    ) -> None:
        self._logger.info("Message received")
