import asyncio
import datetime
import json
from typing import Any, ClassVar

import httpx
import json_api_doc
import openai
from dateutil import parser, tz
from starlette import status
from starlette.background import BackgroundTask

from snowfall.project.junction.plus.service.poc_api import airlines, twilio
from snowfall.stdlib.logging import stdout
from snowfall.stdlib.persistence.redis import types as redis
from snowfall.vendor.junction.go import client


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

    async def handle_prompt(  # noqa: WPS211, WPS210
        self,
        message: str,
        mobile_phone: str,
        redis_client: redis.Client[str],
        junction_client: client.Client,
        twilio_client: twilio.TwilioClient,
    ) -> Any:
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
            await redis_client.delete(
                "ai_message_history:{0}".format(mobile_phone),
            )
            try:
                arguments = json.loads(assistant_message["function_call"]["arguments"])
            except json.JSONDecodeError:
                arguments = {
                    "departureLoc": "Athens",
                    "arrivalLoc": "Thessaloniki",
                    "departure_at": "2023-07-29",
                    "num_of_travelers": 1,
                }
            task = (
                BackgroundTask(
                    fetch_trip_offers_wrapper,
                    arguments["departureLoc"],
                    arguments["arrivalLoc"],
                    arguments["departure_at"],
                    arguments["num_of_travelers"],
                    junction_client,
                    twilio_client,
                    mobile_phone,
                ),
            )
            return [
                (
                    "Alright, I've got all the necessary information. I will fetch you"
                    " an offer for that right away."
                ),
                task[0],
            ]
        if assistant_message["content"] == "irrelevant prompt":
            await redis_client.delete(
                "ai_message_history:{0}".format(mobile_phone),
            )
            return_message = "irrelevant prompt"
        else:
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
        return [return_message, None]


async def get_place(key: str) -> Any:
    async with httpx.AsyncClient() as mobile_client:
        place = await mobile_client.get(
            url="https://superapp.junction.dev/places",
            params={"query[name]": key},
            headers={
                "Content-Type": "application/vnd.api+json",
                "Authorization": (
                    "Bearer"
                    " eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJjbGllbnRfaWQiOiI4NzhjMzg4NS1iYjdlLTRkNjAtODhmMC1lYzllODY4NTI2ZTQiLCJ2ZXJzaW9uIjoiMS4wLjAifQ.FNBpMaTovHfJLK6gdHE8Gc_d7Oy0nHaRYXlILVM9LmuwTu_2Xm0o7HeMhtea6_KS9YhqnyELlLvNQHKTTQXZxv26XMa8RjnalHY_cgrE1PwPu3LrwAxA53NHVrVf55XhwnKNEtBBI7pwBmCvTsAfkPxyYzNU9fLH-rgjn7Zi0BUVjoj75onW6Tud4AWcbNJ2-ZHREri-FV6ADw0_jUIB2wIFoOjyaMjsOcIsSF5lRHqKH6Sq35-fPfs5_GkoRhvpmRln8CGovsNGcLP62StQp_T0S9r09CarfC1s7COdaPiK01uiJtys6H7z9kzxyvOMmr6pPNOcA558bMzt2XGpN43eKmrJHtG658xzaUkWn1fEFe2rAk6RGv5muavCFZ5axyn3UmWKJYwgD_rguujNTIncoHlYCT-8ioAsBW-tDx5sHdApRzAvLA-4RUgVY6h7tsMK5FoSiGt7Ps6YxOAzJN6IojgFJRKYEpXsz7E_T9HhIJy3UIb7sN6RqdpsMK55uBG6t_dd3n2jqBKNjSofxcbqF5sWOXGWpTDIqbILq5YG-TpGPPN9o9AN0Nm8YIiOOcYrq661gaATIlSSBcc_wU1ojrmB1iCYYfQq7BWQDzWFZR4aXYWwGgCJ-gqw6kvnUHMrztX_UXAFR-fsVQmlqsjeQRwgXPtFcZf-hDYBNnY"
                ),
            },
        )
        if place.status_code == status.HTTP_200_OK:
            return place.json()["data"][0]["id"]
        raise RuntimeError("Can't find a place with that name: {0}".format(key))


async def fetch_trip_offers_wrapper(  # noqa: WPS211,
    departure_loc: str,
    arrival_loc: str,
    departure_at: str,
    num_of_travelers: int,
    junction_client: client.Client,
    twilio_client: twilio.TwilioClient,
    receiver_mobile: str,
) -> None:
    try:
        await fetch_trip_offers(
            departure_loc,
            arrival_loc,
            departure_at,
            num_of_travelers,
            junction_client,
            twilio_client,
            receiver_mobile,
        )
    except RuntimeError:
        twilio_client.send_message(
            body="Unable to fetch an offer for the selected trip. Please try again",
            receiver=receiver_mobile,
        )


async def fetch_trip_offers(  # noqa: WPS211,WPS217,WPS210
    departure_loc: str,
    arrival_loc: str,
    departure_at: str,
    num_of_travelers: int,
    junction_client: client.Client,
    twilio_client: twilio.TwilioClient,
    receiver_mobile: str,
) -> None:
    origin = await get_place(departure_loc)
    destination = await get_place(arrival_loc)
    trip_search = await junction_client.trips().create_trip_search(
        origin_id=origin,
        destination_id=destination,
        departure_after=parser.parse(departure_at).replace(tzinfo=tz.tzutc()),
        allowed_segment_types=[],
    )
    await asyncio.sleep(1)
    trips = await junction_client.trips().get_trips_by_trip_search_id(
        trip_search["data"]["id"],
        limit=1,
    )
    if not trips["data"]:
        raise RuntimeError(
            "Couldn't find trips for this trip search: {0}".format(
                trip_search["data"]["id"],
            ),
        )
    offer_search = await junction_client.create_offer_search(
        trip_ids=[trips["data"][0]["id"]],
        passengers_dates_of_birth=[
            datetime.date.fromisoformat("1990-02-03") for _ in range(num_of_travelers)
        ],
        session_token="YMSXrOAhIOdvIbxAmfSt7vJtRBkurNb6",  # noqa: S106
    )
    await asyncio.sleep(5)
    offers = json_api_doc.deserialize(
        await junction_client.get_offers_by_offer_search_id(
            offer_search["data"]["id"],
            limit=1,
            cabin_class=None,
            include=["groups.options", "groups.details"],
        ),
    )
    if not offers:
        raise RuntimeError(
            "Couldn't find offers for this offer search: {0}".format(
                offer_search["data"]["id"],
            ),
        )
    offer_group = offers[0]["groups"][0]
    offer_group_details = offer_group["details"][0]
    offer_group_options = offer_group["options"]
    twilio_client.send_message(
        body=(
            "Operator: {0}\n".format(
                airlines.airlines_mapping.get(offer_group_details["operator"], "N/A"),
            )
            + "Departure time: {0}\n".format(
                datetime.datetime.fromisoformat(
                    offer_group_details["legs"][0]["departureAt"],
                ).strftime(
                    "%m/%d/%Y, %H:%M:%S",
                ),
            )
            + "Options: "
            + "".join(
                [
                    "\n{0} - {1}SEK".format(
                        option["brandName"],
                        option["price"]["amount"],
                    )
                    for option in offer_group_options
                ],
            )
        ),
        receiver=receiver_mobile,
    )
