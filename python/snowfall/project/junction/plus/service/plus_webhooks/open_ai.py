import datetime
import json
from collections.abc import Mapping, Sequence
from typing import Any, ClassVar

import openai

from snowfall.stdlib.logging import stdout


def home_function(*args: Any, **kwargs: Any) -> str:
    return "Do you want to continue with new queries about trip destination?"


def search_flight(
    origin: str,
    destination: str,
    date: str,
    *args: Any,
    **kwargs: Any,
) -> str:
    return "URL for Flight from {0} to {1} on date {2}".format(
        origin,
        destination,
        date,
    )


class AIBot(object):
    _system_setup = """
        You are a travel assistant and you should answer only to travel related questions.
        For anything else, you should respond with "unrelated question" message.
        Currently it is {0}.
        Use dd-mm-yyyy for date format.
        When the user gives you a valid city name, provide the following 3 options as examples
        "1) Top 5 restaurants, 2) I would like to spend
        a day here, 3) Give me a 3 day itinerary"
        Then wait for user's input and answer to the question if it's travel related.
        After that, call the home_function.
        If user wants to find ticket for flight, ask user to specify date,
        the origin valid city name, destination valid city name, then call the search_flight.
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
                "Needs to be called when user wants to book or buy a flight ticket when"
                " date, origin and destination of flight are clear"
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "origin": {
                        "type": "string",
                        "description": "The origin city",
                    },
                    "destination": {
                        "type": "string",
                        "description": "The destination city",
                    },
                    "date": {
                        "type": "string",
                        "description": "Date for flight in format of dd-mm-yyyy",
                    },
                },
                "required": ["origin", "destination", "date"],
            },
        },
    ]

    available_functions: ClassVar[Any] = {
        "home_function": home_function,
        "search_flight": search_flight,
    }

    def __init__(self) -> None:
        self._logger = stdout.get_logger()

    def generate_system_setup(self) -> str:
        return self._system_setup.format(
            datetime.datetime.now(tz=datetime.UTC).strftime("%d-%m-%Y %H:%M"),
        )

    async def handle_prompt(
        self,
        messages: Sequence[Mapping[str, str]],
    ) -> Mapping[str, str]:
        """Get message history from state, append message and send to openai."""
        ai_response = await openai.ChatCompletion.acreate(
            # type: ignore[no-untyped-call]
            model="gpt-3.5-turbo",
            messages=messages,
            functions=self.functions,
            temperature=0.2,  # noqa: WPS432
        )
        assistant_message = ai_response["choices"][0]["message"].to_dict()
        if assistant_message.get("function_call"):
            function_name = assistant_message["function_call"]["name"]
            assistant_arguments = json.loads(
                assistant_message["function_call"]["arguments"],
            )
            return {
                "content": self.available_functions[function_name](
                    **assistant_arguments,
                ),
                "role": "assistant",
            }
        return assistant_message
