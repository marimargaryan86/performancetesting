from collections.abc import Mapping, Sequence
from typing import Any, ClassVar

import openai

from snowfall.stdlib.logging import stdout


class AIBot(object):
    system_setup = """
        You are a travel assistant. The user must give you a valid city name as
        destination and then you should provide any travel information the user asks
        for. After a user provides a valid city name, give the 3 following queries
        examples just to help the user "1) Top 5 restaurants, 2) I would like to spend
        a day here, 3) Give me a 3 day itinerary". If the user doesn't give you a valid
        city name, guide it to do it. The query about a city destination must be a valid
        one related to travel information. If the query is unrelated, guide the user.
        If the user continues to give unrelated queries, return "unrelated questions".
        After you answer user's question, call home function
    """
    initial_message = """
        As your travel assistant I am happy to provide information to improve your travel experience. Please let me know where are you planning to go?
    """
    functions: ClassVar[Any] = []

    def __init__(self) -> None:
        self._logger = stdout.get_logger()

    async def handle_prompt(
        self,
        messages: Sequence[Mapping[str, str]],
    ) -> Mapping[str, str]:
        """Get message history from state, append message and send to openai."""
        ai_response = await openai.ChatCompletion.acreate(  # type: ignore[no-untyped-call]
            model="gpt-3.5-turbo",
            messages=messages,
            functions=self.functions,
            temperature=0.2,  # noqa: WPS432
        )
        return ai_response["choices"][0]["message"].to_dict()
