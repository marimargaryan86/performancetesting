import json
import re
from collections.abc import Mapping
from typing import Any

from nio import AsyncClient, Event, InviteNameEvent, MatrixRoom, RoomMessageText

from snowfall.project.junction.plus.adapter import configuration_vectors, subscribers
from snowfall.project.junction.plus.service.plus_webhooks import open_ai, shortener
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
        ai_bot: open_ai.AIBot,
        shortener_client: shortener.Client,
    ):
        super().__init__(homeserver, user)
        self._redis = redis_client
        self._subscribers = subscribers_client
        self._configuration_vectors = configuration_vectors_client
        self._ai_bot = ai_bot
        self.shortener_client = shortener_client
        self._logger = stdout.get_logger()
        self.add_event_callback(self.message_callback, (RoomMessageText,))
        self.add_event_callback(self.autojoin_room, (InviteNameEvent,))

    async def message_callback(
        self,
        room: MatrixRoom,
        event: Event | RoomMessageText,
    ) -> None:
        if event.sender != room.own_user_id:
            session = self._redis.hash_("ai_assistant_state")
            state_str = await session.get(room.room_id)
            if state_str:
                state: Mapping[str, Any] = json.loads(state_str) or {}
                ai_chat_history = state.get("ai_chat_history", [])
            else:
                ai_chat_history = [
                    {"role": "system", "content": self._ai_bot.generate_system_setup()},
                ]
                state = {
                    "ai_chat_history": ai_chat_history,
                }
            ai_chat_history.append({"role": "user", "content": event.body})
            assistant_message = await self._ai_bot.handle_prompt(
                messages=ai_chat_history,
                search_url="",
                shortener_client=self.shortener_client,
            )
            ai_chat_history.append(assistant_message)
            await session.put(room.room_id, json.dumps(state))

            await self.room_send(
                room_id=room.room_id,
                message_type="m.room.message",
                content={
                    "msgtype": "m.text",
                    "body": (
                        assistant_message["content"]
                        if isinstance(assistant_message["content"], str)
                        else ""
                    ),
                },
            )

        self._logger.info("Message received")

    async def autojoin_room(
        self,
        room: MatrixRoom,
        event: Event,
    ) -> None:
        username = re.findall("@(.*?):", event.sender)[0]
        cv = await self._configuration_vectors.get(
            identifier=username,
            selector="in_app_notification_user",
        )
        subscriber = await self._subscribers.find_from_reseller(
            cv.reseller_id,
            room.name,
        )
        await self.join(room.room_id)
        session = self._redis.hash_("ai_assistant_state")
        ai_chat_history = [
            {"role": "system", "content": self._ai_bot.generate_system_setup()},
            {"role": "assistant", "content": self._ai_bot.initial_message},
        ]
        state = {
            "ai_chat_history": ai_chat_history,
        }
        await session.put(room.room_id, json.dumps(state))
        await self.room_send(
            room_id=room.room_id,
            message_type="m.room.message",
            content={
                "msgtype": "m.text",
                "body": self._ai_bot.initial_message,
            },
        )
        self._logger.info(
            "Joined room",
            room_name=room.name,
            room_id=room.room_id,
            subscriber=subscriber.id,
        )

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
