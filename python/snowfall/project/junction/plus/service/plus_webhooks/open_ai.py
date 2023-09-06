from collections.abc import Mapping, Sequence
from typing import Any, ClassVar

import openai

from snowfall.stdlib.logging import stdout


def home_function() -> str:
    return "Do you want to continue with new queries about trip destination?"


class AIBot(object):
    system_setup = """
        You are a travel assistant and you should answer only to travel related questions.
        For anything else, you should respond with "unrelated question" message.
        When the user gives you a valid city name, provide the following 3 options as examples
        "1) Top 5 restaurants, 2) I would like to spend
        a day here, 3) Give me a 3 day itinerary"
        Then wait for user's input and answer to the question if it's travel related.
        After that, call the home_function.
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
    ]

    available_functions: ClassVar[Any] = {
        "home_function": home_function,
    }

    def __init__(self) -> None:
        self._logger = stdout.get_logger()

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
            return {"content": self.available_functions[function_name]()}
        return assistant_message
