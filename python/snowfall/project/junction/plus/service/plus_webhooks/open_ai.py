import datetime
import json
from collections.abc import Sequence
from contextlib import suppress
from gettext import gettext as _
from typing import Any, ClassVar, cast

import httpx
import openai
from openai.types import chat

from snowfall.project.junction.plus.service.plus_webhooks import shortener
from snowfall.stdlib.logging import stdout


async def home_function(*args: Any, **kwargs: Any) -> str:
    return "Do you want to continue with new queries about trip destination?"


async def search_flight(
    search_url: str,
    shortener_client: shortener.Client,
    *args: Any,
    **kwargs: Any,
) -> str:
    if not search_url:
        return _("Travel assistant can't help you with ticket search")
    short_link = search_url
    if len(search_url) > 30:  # noqa: WPS432
        with suppress(httpx.HTTPStatusError):
            short_link = await shortener_client.shorten_link(search_url)

    return _("Please book your flights here: ") + short_link


_TEMPERATURE = 0.2


class AIBot:
    _system_setup = """
        You are a travel assistant and you should answer only to travel related questions.
        For anything else, you should respond with "unrelated question" message.
        Currently it is {0}.
        Use dd-mm-yyyy for date format.
        When the user mentions airport, use city where that airport is located and offer 3 options as example.
        When the user gives you a valid city name, provide the following 3 options as examples
        "1) Top 5 restaurants, 2) I would like to spend
        a day here, 3) Give me a 3 day itinerary"
        Then wait for user's input and answer to the question if it's travel related.
        After that, call the home_function.
        If user wants to find ticket for flight call the search_flight.
        When the user wants activities provide the following options as example
        "1) Hotels, 2) Restaurants, 3) Museums, 4) Concerts, 5) Nightlife (bars, clubs), 6) Hiking"
        Then wait for user's input and answer to the question if it's from mentioned options.
        If your answer includes suggestion about place or activity always include url to them
        and add at the end of whole message
        "This disclaimer serves to inform users about the limitations of the information provided and encourages
        them to take responsible steps to verify the accuracy and legitimacy of links and information.
    """
    initial_message = """
        Welcome to your travel assistant. For which city are you interested about?
    """
    functions: ClassVar[Any] = [
        {
            "name": "home_function",
            "description": (
                "Reset chat history and disable ai assistant. Needs to be called after"
                " a user doesn't need the travel assistant any more"
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "no_params": {"type": "null"},
                },
            },
        },
        {
            "name": "search_flight",
            "description": (
                "Needs to be called when user wants to book or buy a flight ticket"
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "no_params": {"type": "null"},
                },
            },
        },
    ]

    available_functions: ClassVar[Any] = {
        "home_function": home_function,
        "search_flight": search_flight,
    }

    def __init__(self, ai_client: openai.AsyncClient) -> None:
        self._ai_client = ai_client
        self._logger = stdout.get_logger()

    def generate_system_setup(self) -> str:
        return self._system_setup.format(
            datetime.datetime.now(tz=datetime.UTC).strftime("%d-%m-%Y %H:%M"),
        )

    async def handle_prompt(
        self,
        messages: Sequence[chat.ChatCompletionMessageParam],
        search_url: str,
        shortener_client: shortener.Client,
    ) -> chat.ChatCompletionMessageParam:
        """Get message history from state, append message and send to openai."""
        ai_response = await self._ai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=list(messages),
            functions=self.functions,
            temperature=_TEMPERATURE,
        )
        assistant_message = ai_response.choices[0].message
        if assistant_message.function_call:
            function_name = assistant_message.function_call.name
            assistant_arguments = json.loads(
                assistant_message.function_call.arguments,
            )
            return {
                "content": await self.available_functions[function_name](
                    search_url=search_url,
                    shortener_client=shortener_client,
                    **assistant_arguments,
                ),
                "role": "assistant",
            }
        return cast(chat.ChatCompletionMessageParam, assistant_message.model_dump())
