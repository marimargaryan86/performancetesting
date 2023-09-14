import datetime
import json
import time
from collections.abc import Mapping, Sequence
from gettext import gettext as _
from typing import Any

from snowfall.project.junction.plus.adapter import orders, subscribers
from snowfall.project.junction.plus.notification_channels.order_utils import (
    compress_flights,
)
from snowfall.project.junction.plus.notification_channels.whatsapp import (
    transform_trip_details,
)
from snowfall.project.junction.plus.service.notifications.v1alpha import models_pb2
from snowfall.project.junction.plus.service.plus_webhooks import open_ai
from snowfall.stdlib.format import protobuf
from snowfall.stdlib.logging import stdout
from snowfall.stdlib.persistence.redis import types as redis

action_menu = _("Please select one of the following options")

trip_details_menu = _(
    "To enable auto check-in and save time at the airport please click the"
    " *Check-in* button below. For further options please click on the *Main Menu*"
    " button.",
)


class MessageHandler(object):
    def __init__(
        self,
        redis_client: redis.Client[str],
        cache_ttl: datetime.timedelta,
        ai_bot: open_ai.AIBot,
    ) -> None:
        self._redis = redis_client
        # Not going to use it now but in the future we can decide to
        # reset the state of whatsapp conversation after some time
        self._default_ttl = cache_ttl
        self._ai_bot = ai_bot
        self._logger = stdout.get_logger()

    async def handle_message(  # noqa: WPS211,WPS210
        self,
        message: str,
        message_key: str,
        subscriber: models_pb2.Subscriber,
        subscribers_client: subscribers.Client,
        orders_client: orders.Client,
    ) -> Sequence[str]:
        subscriber_state = await self.get_state("subscriber_state", subscriber)
        ai_assistant_state = await self.get_state("ai_assistant_state", subscriber)
        if (  # noqa: WPS337
            subscriber_state.get("last_handler")
            in {"upcoming_trips", "upcoming_trip_details"}
            and message.isdigit()
        ):
            message_key = message
            message = "upcoming trip details"
        message_handler = message_handlers(message.lower())
        if (  # noqa: WPS337
            ai_assistant_state.get("ai_enabled")
            and message_handler is not handle_unknown
        ):
            await self.delete_state("ai_assistant_state", subscriber)
        response = await message_handler(
            subscriber=subscriber,
            subscribers_client=subscribers_client,
            orders_client=orders_client,
            message=message,
            message_key=message_key,
            ai_bot=self._ai_bot,
            redis_client=self._redis,
        )
        subscriber_state["last_message"] = message
        subscriber_state["last_response"] = response[0]
        subscriber_state["last_handler"] = message_handler.__name__
        await self.store_state("subscriber_state", subscriber, subscriber_state)
        return response

    async def store_state(
        self,
        hash_name: str,
        subscriber: models_pb2.Subscriber,
        hash_value: Mapping[str, str],
    ) -> None:
        session = self._redis.hash_(hash_name)
        await session.put(subscriber.phone_number.e164_number, json.dumps(hash_value))

    async def get_state(
        self,
        hash_name: str,
        subscriber: models_pb2.Subscriber,
    ) -> Any:
        session = self._redis.hash_(hash_name)
        state = await session.get(subscriber.phone_number.e164_number)
        if state:
            return json.loads(state)
        return {}

    async def delete_state(
        self,
        hash_name: str,
        subscriber: models_pb2.Subscriber,
    ) -> None:
        session = self._redis.hash_(hash_name)
        await session.delete(subscriber.phone_number.e164_number)


# TODO: Change this to class method and use it as decorator to register handlers
def message_handlers(fun: str) -> Any:
    return {
        "subscribe": subscribe,
        "unsubscribe": unsubscribe,
        "trip details": trip_details,
        "upcoming trips": upcoming_trips,
        "main menu": main_menu,
        "check-in": check_in,
        "upcoming trip details": upcoming_trip_details,
        "travel assistant": travel_assistant,
    }.get(fun, handle_unknown)


async def unsubscribe(
    subscriber: models_pb2.Subscriber,
    subscribers_client: subscribers.Client,
    **kwargs: Any,
) -> Sequence[str]:  # noqa: WPS473
    unsubscribe_status = await subscribers_client.unsubscribe(subscriber.id)
    if unsubscribe_status:
        return [
            _(
                "You have unsubscribed from WhatsApp and will no longer receive"
                " notifications regarding travel information. If you wish to"
                " resubscribe please click the Subscribe button below.",
            ),
        ]
    raise RuntimeError("error while unsubscribing with id: {0}".format(subscriber.id))


async def subscribe(
    subscriber: models_pb2.Subscriber,
    subscribers_client: subscribers.Client,
    **kwargs: Any,
) -> Sequence[str]:  # noqa: WPS473
    subscribe_status = await subscribers_client.subscribe(subscriber.id)
    if subscribe_status:
        return [
            _(
                "You have successfully subscribed on WhatsApp!"
                " You can now receive notifications regarding travel information.",
            ),
            action_menu,
        ]
    raise RuntimeError("error while subscribing with id: {0}".format(subscriber.id))


async def trip_details(
    orders_client: orders.Client,
    message_key: str,
    redis_client: redis.Client[str],
    **kwargs: Any,
) -> Sequence[str]:  # noqa: WPS473
    order = None
    if message_key:
        order_id = await get_order_id_by_message_id(redis_client, message_key)
        if order_id:
            order = await orders_client.get(order_id)
    if order is None:
        return [
            _("Sorry there are no details available for this trip."),
            action_menu,
        ]
    return [
        transform_trip_details(order),
        trip_details_menu,
    ]


async def upcoming_trips(  # noqa: WPS210
    subscriber: models_pb2.Subscriber,
    orders_client: orders.Client,
    redis_client: redis.Client[str],
    **kwargs: Any,
) -> Sequence[str]:  # noqa: WPS473
    await redis_client.delete("upcoming_trips_{0}".format(subscriber.id))
    session = redis_client.hash_("upcoming_trips_{0}".format(subscriber.id))

    subscriber_orders = await orders_client.find(subscriber.id)
    processed_bookings_message = ""
    counter = 1
    if subscriber_orders:
        for order in subscriber_orders:
            processed_bookings = compress_flights(
                [
                    booking.value
                    for booking in order.bookings
                    if booking.value.DESCRIPTOR.name == "AirBooking"
                    and booking.value.departure_at.seconds > int(time.time())
                ],
            )
            if processed_bookings:
                await session.put(str(counter), order.id)
                processed_bookings_message += _(
                    "\n\n{0}. ".format(counter)
                    + "\n    ".join(
                        [
                            "*{0} > {1} ({2})*".format(
                                booking.origin,
                                booking.destination,
                                protobuf.protobuf_to_datetime(
                                    booking.departure_at,
                                ).strftime("%d/%m/%Y"),
                            )
                            for booking in processed_bookings
                        ],
                    ),
                )
                counter += 1
        if processed_bookings_message:
            return [
                _(
                    "*Upcoming trips*\nUse one of the menu options below by typing the"
                    " corresponding number for more information"
                    + processed_bookings_message,
                ),
            ]
    return [
        _("*It looks like you have no upcoming trips at the moment.*"),
        action_menu,
    ]


async def upcoming_trip_details(
    subscriber: models_pb2.Subscriber,
    orders_client: orders.Client,
    message_key: str,
    redis_client: redis.Client[str],
    **kwargs: Any,
) -> Sequence[str]:  # noqa: WPS473
    session = redis_client.hash_("upcoming_trips_{0}".format(subscriber.id))
    order_id = await session.get(message_key)
    if not order_id:
        return [_("Invalid option. Please try again")]
    return [
        transform_trip_details(await orders_client.get(order_id)),
        trip_details_menu,
    ]


async def travel_assistant(
    subscriber: models_pb2.Subscriber,
    ai_bot: open_ai.AIBot,
    redis_client: redis.Client[str],
    **kwargs: Any,
) -> Sequence[str]:
    session = redis_client.hash_("ai_assistant_state")
    ai_chat_history = [
        {"role": "system", "content": ai_bot.generate_system_setup()},
        {"role": "assistant", "content": ai_bot.initial_message},
    ]
    state = {
        "ai_chat_history": ai_chat_history,
        "ai_enabled": True,
    }
    await session.put(subscriber.phone_number.e164_number, json.dumps(state))
    return [_(ai_bot.initial_message)]


async def check_in(
    **kwargs: Any,
) -> Sequence[str]:
    return [
        _("Check-in feature is not implemented yet."),
        action_menu,
    ]


async def handle_unknown(
    subscriber: models_pb2.Subscriber,
    message: str,
    ai_bot: open_ai.AIBot,
    redis_client: redis.Client[str],
    **kwargs: Any,
) -> Sequence[str]:
    session = redis_client.hash_("ai_assistant_state")
    state_str = await session.get(subscriber.phone_number.e164_number)
    if state_str:
        state: Mapping[str, Any] = json.loads(state_str) or {}
        if state.get("ai_enabled"):
            # We should associate with message id to not bind those keywords, but we can do it after refactoring and async reply on chatbot.
            if message.lower() in {"yes", "no"}:
                await session.delete(subscriber.phone_number.e164_number)
                if message == "yes":
                    return await travel_assistant(subscriber, ai_bot, redis_client)
                return [action_menu]
            ai_chat_history = state.get("ai_chat_history", [])
            ai_chat_history.append({"role": "user", "content": message})
            assistant_message = await ai_bot.handle_prompt(ai_chat_history)
            ai_chat_history.append(assistant_message)
            await session.put(subscriber.phone_number.e164_number, json.dumps(state))
            return [_(assistant_message["content"])]
    return [
        _("Sorry I didn't understand your message."),
        action_menu,
    ]


async def main_menu(
    *args: Any,
    **kwargs: Any,
) -> Sequence[str]:
    return [action_menu]


async def get_order_id_by_message_id(
    redis_client: redis.Client[str],
    sid: str,
) -> str:
    session = redis_client.hash_("message_id_order_id")
    order_id = await session.get(sid)
    return order_id or ""
