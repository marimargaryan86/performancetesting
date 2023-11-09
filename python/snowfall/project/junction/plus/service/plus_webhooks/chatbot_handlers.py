import datetime
import json
import time
from collections.abc import Mapping, Sequence
from gettext import gettext as _
from typing import Any, TypeAlias

import grpc

from snowfall.project.junction.plus.adapter import (
    flight_delay_predictor,
    orders,
    subscribers,
)
from snowfall.project.junction.plus.adapter.format import proto_to_route_identifier
from snowfall.project.junction.plus.notification_channels.order_utils import (
    compress_flights,
)
from snowfall.project.junction.plus.notification_channels.whatsapp import (
    transform_trip_details,
)
from snowfall.project.junction.plus.service.notifications.v1alpha import models_pb2
from snowfall.project.junction.plus.service.plus_webhooks import open_ai, shortener
from snowfall.stdlib.format import protobuf
from snowfall.stdlib.logging import stdout
from snowfall.stdlib.persistence.redis import types as redis

action_menu = {
    "message": _("Please select one of the following options"),
}


trip_details_menu = {
    "message": _(
        "To enable auto check-in and save time at the airport please click on the"
        " *Check-in* button below. If you would like to plan this trip please click on"
        " the Plan this trip button. For further options please click on the *Main"
        " Menu* button.",
    ),
}

_HandlersResponse: TypeAlias = Sequence[Mapping[str, Any]]


class MessageHandler(object):
    def __init__(
        self,
        redis_client: redis.Client[str],
        cache_ttl: datetime.timedelta,
        ai_bot: open_ai.AIBot,
        shortener_client: shortener.Client,
        flight_predictions_client: flight_delay_predictor.Client,
    ) -> None:
        self._redis = redis_client
        # Not going to use it now but in the future we can decide to
        # reset the state of whatsapp conversation after some time
        self._default_ttl = cache_ttl
        self._ai_bot = ai_bot
        self._shortener_client = shortener_client
        self._flight_predictions_client = flight_predictions_client
        self._logger = stdout.get_logger()

    async def handle_message(
        self,
        message: str,
        message_key: str,
        subscriber: models_pb2.Subscriber,
        configuration_vector: models_pb2.ConfigurationVector,
        subscribers_client: subscribers.Client,
        orders_client: orders.Client,
    ) -> _HandlersResponse:
        subscriber_state = await self.get_cache(
            hash_name="subscriber_state",
            hash_key=subscriber.phone_number.e164_number,
        )
        ai_assistant_state = await self.get_cache(
            hash_name="ai_assistant_state",
            hash_key=subscriber.phone_number.e164_number,
        )
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
            await self.delete_cache(
                "ai_assistant_state",
                subscriber.phone_number.e164_number,
            )
        try:
            response = await message_handler(
                subscriber=subscriber,
                configuration_vector=configuration_vector,
                flight_predictions_client=self._flight_predictions_client,
                subscribers_client=subscribers_client,
                orders_client=orders_client,
                message=message,
                message_key=message_key,
                ai_bot=self._ai_bot,
                redis_client=self._redis,
                shortener_client=self._shortener_client,
                logger=self._logger,
            )
        except RuntimeError:
            return [
                {
                    "message": _(
                        "There is an issue retrieving the requested data at the moment."
                        " Please try again later",
                    ),
                },
            ]
        subscriber_state["last_message"] = message
        subscriber_state["last_response"] = response[0]["message"]
        subscriber_state["last_handler"] = message_handler.__name__
        await self.store_cache(
            "subscriber_state",
            subscriber.phone_number.e164_number,
            json.dumps(subscriber_state),
        )
        return response

    async def store_cache(
        self,
        hash_name: str,
        hash_key: str,
        hash_value: str,
    ) -> None:
        session = self._redis.hash_(hash_name)
        await session.put(hash_key, hash_value)

    async def get_cache(
        self,
        hash_name: str,
        hash_key: str,
    ) -> Any:
        session = self._redis.hash_(hash_name)
        hash_value = await session.get(hash_key)
        if hash_value:
            return json.loads(hash_value)
        return {}

    async def delete_cache(
        self,
        hash_name: str,
        hash_key: str,
    ) -> None:
        session = self._redis.hash_(hash_name)
        await session.delete(hash_key)


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
        "plan this trip": plan_selected_trip,
    }.get(fun, handle_unknown)


async def unsubscribe(
    subscriber: models_pb2.Subscriber,
    subscribers_client: subscribers.Client,
    **kwargs: Any,
) -> _HandlersResponse:
    unsubscribe_status = await subscribers_client.unsubscribe(subscriber.id)
    if unsubscribe_status:
        return [
            {
                "message": _(
                    "You have unsubscribed from WhatsApp and will no longer receive"
                    " notifications regarding travel information. If you wish to"
                    " resubscribe please click the Subscribe button below.",
                ),
            },
        ]
    raise RuntimeError("error while unsubscribing with id: {0}".format(subscriber.id))


async def subscribe(
    subscriber: models_pb2.Subscriber,
    subscribers_client: subscribers.Client,
    **kwargs: Any,
) -> _HandlersResponse:
    subscribe_status = await subscribers_client.subscribe(subscriber.id)
    if subscribe_status:
        return [
            {
                "message": _(
                    "You have successfully subscribed on WhatsApp!"
                    " You can now receive notifications regarding travel information.",
                ),
            },
            action_menu,
        ]
    raise RuntimeError("error while subscribing with id: {0}".format(subscriber.id))


async def trip_details(
    orders_client: orders.Client,
    message_key: str,
    redis_client: redis.Client[str],
    flight_predictions_client: flight_delay_predictor.Client,
    logger: stdout.Logger,
    **kwargs: Any,
) -> _HandlersResponse:
    order = None
    if message_key:
        session = redis_client.hash_("message_id_order_id")
        order_id = await session.get(message_key) or ""
        if order_id:
            order = await orders_client.get(order_id)
    if order is None:
        return [
            {
                "message": _("Sorry there are no details available for this trip."),
            },
            action_menu,
        ]
    try:
        delays = await flight_predictions_client.predict_delays(
            [
                flight_delay_predictor.Flight(
                    flight_number=proto_to_route_identifier(
                        booking.value.route_identifier,
                    ),
                    scheduled_departure_at=protobuf.protobuf_to_datetime(
                        booking.value.departure_at,
                    ).strftime("%Y-%m-%dT%H:%M:%SZ"),
                )
                for booking in order.bookings
            ],
        )
    except grpc.aio.AioRpcError:
        logger.exception("Failed to get flight delay prediction")
        delays = None
    return [
        {
            "message": transform_trip_details(order, delays),
        },
        {
            **trip_details_menu,
            "cache": {
                "hash": "message_id_order_id",
                "value": order.id,
            },
        },
    ]


async def upcoming_trips(
    subscriber: models_pb2.Subscriber,
    orders_client: orders.Client,
    redis_client: redis.Client[str],
    **kwargs: Any,
) -> _HandlersResponse:
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
                                booking.origin.name,
                                booking.destination.name,
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
                {
                    "message": _(
                        "*Upcoming trips*\nUse one of the menu options below by typing"
                        " the corresponding number for more information"
                        + processed_bookings_message,
                    ),
                },
            ]
    return [
        {
            "message": _("*It looks like you have no upcoming trips at the moment.*"),
        },
        action_menu,
    ]


async def upcoming_trip_details(
    subscriber: models_pb2.Subscriber,
    orders_client: orders.Client,
    message_key: str,
    redis_client: redis.Client[str],
    flight_predictions_client: flight_delay_predictor.Client,
    logger: stdout.Logger,
    **kwargs: Any,
) -> _HandlersResponse:
    session = redis_client.hash_("upcoming_trips_{0}".format(subscriber.id))
    order_id = await session.get(message_key)
    if not order_id:
        return [
            {
                "message": _("Invalid option. Please try again"),
            },
        ]
    order = await orders_client.get(order_id)
    try:
        delays = await flight_predictions_client.predict_delays(
            [
                flight_delay_predictor.Flight(
                    flight_number=proto_to_route_identifier(
                        booking.value.route_identifier,
                    ),
                    scheduled_departure_at=protobuf.protobuf_to_datetime(
                        booking.value.departure_at,
                    ).strftime("%Y-%m-%dT%H:%M:%SZ"),
                )
                for booking in order.bookings
            ],
        )
    except grpc.aio.AioRpcError:
        logger.exception("Failed to get flight delay prediction")
        delays = None
    return [
        {
            "message": transform_trip_details(order, delays),
        },
        {
            **trip_details_menu,
            "cache": {
                "hash": "message_id_order_id",
                "value": order_id,
            },
        },
    ]


async def travel_assistant(
    subscriber: models_pb2.Subscriber,
    ai_bot: open_ai.AIBot,
    redis_client: redis.Client[str],
    **kwargs: Any,
) -> _HandlersResponse:
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
    return [
        {
            "message": _(ai_bot.initial_message),
        },
    ]


async def plan_selected_trip(
    subscriber: models_pb2.Subscriber,
    configuration_vector: models_pb2.ConfigurationVector,
    orders_client: orders.Client,
    ai_bot: open_ai.AIBot,
    message_key: str,
    redis_client: redis.Client[str],
    shortener_client: shortener.Client,
    **kwargs: Any,
) -> _HandlersResponse:
    if message_key:
        session = redis_client.hash_("message_id_order_id")
        order_id = await session.get(message_key) or ""
        if order_id:
            order = await orders_client.get(order_id)
            processed_bookings = compress_flights(
                [
                    booking.value
                    for booking in order.bookings
                    if booking.value.DESCRIPTOR.name == "AirBooking"
                    and booking.value.departure_at.seconds > int(time.time())
                ],
            )
            if processed_bookings:
                session = redis_client.hash_("ai_assistant_state")
                ai_chat_history = [
                    {"role": "system", "content": ai_bot.generate_system_setup()},
                    {
                        "role": "user",
                        "content": "Airport - {0}".format(
                            processed_bookings[0].destination.name,
                        ),
                    },
                ]
                assistant_message = await ai_bot.handle_prompt(
                    messages=ai_chat_history,
                    search_url=configuration_vector.search_url,
                    shortener_client=shortener_client,
                )
                ai_chat_history.append(assistant_message)
                state = {
                    "ai_chat_history": ai_chat_history,
                    "ai_enabled": True,
                }
                await session.put(
                    subscriber.phone_number.e164_number,
                    json.dumps(state),
                )
                return [
                    {
                        "message": _(assistant_message["content"]),
                    },
                ]
    return [
        {
            "message": _("Sorry, this trip can't be planned"),
        },
        action_menu,
    ]


async def check_in(
    **kwargs: Any,
) -> _HandlersResponse:
    # TODO: After test change back to unimplemented text message
    raise RuntimeError("Check-in feature is not implemented yet.")


async def handle_unknown(
    subscriber: models_pb2.Subscriber,
    configuration_vector: models_pb2.ConfigurationVector,
    message: str,
    ai_bot: open_ai.AIBot,
    redis_client: redis.Client[str],
    shortener_client: shortener.Client,
    **kwargs: Any,
) -> _HandlersResponse:
    session = redis_client.hash_("ai_assistant_state")
    state_str = await session.get(subscriber.phone_number.e164_number)
    if state_str:
        state: Mapping[str, Any] = json.loads(state_str) or {}
        if state.get("ai_enabled"):
            # We should associate with message id to not bind those keywords, but we can do it after refactoring and async reply on chatbot.
            if message.lower() in {"i need more help", "that's all for now"}:
                await session.delete(subscriber.phone_number.e164_number)
                if message.lower() == "i need more help":
                    return await travel_assistant(subscriber, ai_bot, redis_client)
                return [
                    {
                        "message": _("Great! We are here"),
                    },
                    action_menu,
                ]
            ai_chat_history = state.get("ai_chat_history", [])
            ai_chat_history.append({"role": "user", "content": message})
            assistant_message = await ai_bot.handle_prompt(
                messages=ai_chat_history,
                search_url=configuration_vector.search_url,
                shortener_client=shortener_client,
            )
            ai_chat_history.append(assistant_message)
            await session.put(subscriber.phone_number.e164_number, json.dumps(state))
            return [
                {
                    "message": _(assistant_message["content"]),
                },
            ]
    return [
        {
            "message": _("Sorry I didn't understand your message."),
        },
        action_menu,
    ]


async def main_menu(
    *args: Any,
    **kwargs: Any,
) -> _HandlersResponse:
    return [action_menu]
