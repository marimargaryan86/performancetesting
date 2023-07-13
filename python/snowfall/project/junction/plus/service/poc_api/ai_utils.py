import json
from typing import Any, ClassVar

import openai

from snowfall.stdlib.logging import stdout
from snowfall.stdlib.persistence.redis import types as redis


class AIBot(object):
    system_setup = """
        You are a travel planner.
        Users will prompt you with their trip requests and you will interpret these into the follow data structure:
        {
        DepartureLoc: {departureLoc},
        ArrivalLoc: {ArrivalLoc},
        DepartureAt: {departureAt},
        NumTravellers: {numTravellers}
        }

        If you are missing the information to any of these items. Ask the user for them. You cannot let them blank.
        When you are able to complete the data structure, suggest the usage of a function

        If the user prompts are completely irrelevant with that scope, respond with the following message "irrelevant prompt"
        """
    functions: ClassVar[Any] = [
        {
            "name": "fetch_trip_offers",
            "description": (
                "Fetch trip offers for given set of origin, destination, date and"
                " number of passengers"
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "departureLoc": {
                        "type": "string",
                        "description": "The departure city of the trip",
                    },
                    "arrivalLoc": {
                        "type": "string",
                        "description": "The arrival city of the trip",
                    },
                    "departure_at": {
                        "type": "string",
                        "description": "The departure date of the trip.",
                    },
                    "num_of_travelers": {
                        "type": "integer",
                        "description": (
                            "The number of the travelers that this trip is about."
                        ),
                    },
                },
                "required": [
                    "departureLoc",
                    "arrivalLoc",
                    "departure_at",
                    "num_of_travelers",
                ],
            },
        },
    ]

    def __init__(self) -> None:
        self._logger = stdout.get_logger()

    async def handle_prompt(
        self,
        message: str,
        mobile_phone: str,
        redis_client: redis.Client[str],
    ) -> str:
        cached_message_history = await redis_client.get(
            "ai_message_history:{0}".format(mobile_phone),
        )
        if cached_message_history:
            message_history = json.loads(cached_message_history)
        else:
            message_history = [{"role": "system", "content": self.system_setup}]

        message_history.append({"role": "user", "content": message})
        ai_response = await openai.ChatCompletion.acreate(  # type: ignore[no-untyped-call]
            model="gpt-3.5-turbo",
            messages=message_history,
            functions=self.functions,
        )
        assistant_message = ai_response["choices"][0]["message"].to_dict()
        if assistant_message.get("function_call"):
            # Call function with assistant_message["function_call"]["arguments"]
            # and return the results
            message_history = []
            return_message = json.dumps(assistant_message["function_call"]["arguments"])
        elif assistant_message["content"] == "irrelevant prompt":
            # Return the home message from chatbot_utils
            message_history = []
            return_message = "irrelevant prompt"
        else:
            # Return the assistant_message["content"]
            message_history.append(assistant_message)
            return_message = json.dumps(assistant_message["content"])
        await redis_client.put(
            "ai_message_history:{0}".format(mobile_phone),
            json.dumps(message_history),
        )
        self._logger.info(
            "AI bot response",
            response=return_message,
        )
        return return_message
