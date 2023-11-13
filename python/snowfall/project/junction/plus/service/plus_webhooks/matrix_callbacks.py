from nio import AsyncClient, Event, InviteNameEvent, MatrixRoom, RoomMessageText

from snowfall.project.junction.plus.adapter import configuration_vectors, subscribers
from snowfall.stdlib.logging import stdout
from snowfall.stdlib.persistence.redis import types as redis


class MatrixChatbot(AsyncClient):
    def __init__(
        self,
        homeserver: str,
        user: str,
        redis_client: redis.Client[str],
        subscribers_client: subscribers.Client,
        configuration_vectors_client: configuration_vectors.Client,
    ):
        super().__init__(homeserver, user)
        self._redis = redis_client
        self._subscribers = subscribers_client
        self._configuration_vectors = configuration_vectors_client
        self._logger = stdout.get_logger()
        self.add_event_callback(self.message_callback, (RoomMessageText,))
        self.add_event_callback(self.autojoin_room, (InviteNameEvent,))

    async def message_callback(
        self,
        room: MatrixRoom,
        event: Event,
    ) -> None:
        self._logger.info("Message received")

    async def autojoin_room(
        self,
        room: MatrixRoom,
        event: Event,
    ) -> None:
        await self.join(room.room_id)
        self._logger.info("Joined room", room_name=room.name, room_id=room.room_id)

    async def login_bot(self, bot_password: str) -> None:
        self._logger.info(str(await self.login(bot_password)))

    async def run_bot(self, bot_password: str) -> None:
        await self.login_bot(bot_password)
        await self.sync_forever(
            first_sync_filter={
                "room": {
                    "timeline": {
                        "types": ["m.room.message"],
                        "limit": 0,
                    },
                },
            },
        )
