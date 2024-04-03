import asyncio
import datetime
import json
from typing import Any, ClassVar

import httpx
import json_api_doc
import openai
from dateutil import parser, tz
from starlette import exceptions, status

from snowfall.project.junction.plus.service.poc_api import (
    airlines,
    chatbot_utils,
    twilio,
)
from snowfall.stdlib.logging import stdout
from snowfall.stdlib.persistence.redis import types as redis
from snowfall.vendor.junction.go import client

_TEMPERATURE = 0.6
_TWILIO_BODY_LENGTH = 1600


class AIBot:
    system_setup = """
        You are an AI travel assistant dedicated to creating personalized travel recommendations.
Your role is to help users find the best travel options based on their specific interests but also to give suggestions if the user does not give you enough information until you are able to fill out the fetch_trip_offers function parameters.
Engage in a conversation with the user, who wants assistance in planning a trip and desires recommendations for activities like visiting museums, shopping, enjoying beaches, checking the weather, and finding suitable hotels based on their budget. Provide tailored suggestions, consider preferences, and offer helpful information to ensure a memorable travel experience. Avoid creating links to anything.
If the user gives you a total budget try to find a prefect holiday or break manageable within that budget.
Check weather conditions in case the users asks you to find a hot climate or a chilled one.
If the user is unsure of any given suggestion,  comfort the user with positive messaging.
The year is 2023
        If the request from the user is unrelated with travel planning, please respond
        only with the text with "irrelevant prompt"
        in your answers, never exceed the 1500 characters
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

    def __init__(self, ai_client: openai.AsyncClient) -> None:
        self._ai_client = ai_client
        self._logger = stdout.get_logger()

    async def handle_prompt(  # noqa: WPS217
        self,
        message: str,
        mobile_phone: str,
        redis_client: redis.Client[str],
        junction_client: client.Client,
        twilio_client: twilio.TwilioClient,
    ) -> None:
        cached_message_history = await redis_client.get(
            "ai_message_history:{0}".format(mobile_phone),
        )
        if cached_message_history:
            message_history = json.loads(cached_message_history)
        else:
            message_history = [{"role": "system", "content": self.system_setup}]

        message_history.append({"role": "user", "content": message})
        ai_response = await self._ai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=message_history,
            functions=self.functions,
            temperature=_TEMPERATURE,
        )
        assistant_message = ai_response.choices[0].message
        if assistant_message.function_call:
            await redis_client.delete(
                "ai_message_history:{0}".format(mobile_phone),
            )
            try:
                arguments = json.loads(assistant_message.function_call.arguments)
            except json.JSONDecodeError:
                arguments = {
                    "departureLoc": "Athens",
                    "arrivalLoc": "Thessaloniki",
                    "departure_at": "2023-07-29",
                    "num_of_travelers": 1,
                }
            await fetch_trip_offers_wrapper(
                arguments["departureLoc"],
                arguments["arrivalLoc"],
                arguments["departure_at"],
                arguments["num_of_travelers"],
                junction_client,
                twilio_client,
                mobile_phone,
            )
        elif assistant_message.content == "irrelevant prompt":
            await redis_client.delete(
                "ai_message_history:{0}".format(mobile_phone),
            )
            twilio_client.send_message(
                body=chatbot_utils.home_message(),
                receiver=mobile_phone,
            )
        else:
            message_history.append(assistant_message.model_dump())
            await redis_client.put(
                "ai_message_history:{0}".format(mobile_phone),
                json.dumps(message_history),
            )
            twilio_client.send_message(
                body=(
                    assistant_message.content[:_TWILIO_BODY_LENGTH]
                    if assistant_message.content
                    else ""
                ),
                receiver=mobile_phone,
            )


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


async def fetch_trip_offers_wrapper(  # ,
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


async def fetch_trip_offers(  # noqa: WPS217
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
    await asyncio.sleep(2)
    trips = await junction_client.trips().get_trips_by_trip_search_id(
        trip_search["data"]["id"],
    )
    if not trips["data"]:
        raise RuntimeError(
            "Couldn't find trips for this trip search: {0}".format(
                trip_search["data"]["id"],
            ),
        )
    offers_searches = await asyncio.gather(
        *(
            junction_client.create_offer_search(
                trip_ids=[trip["id"]],
                passengers_dates_of_birth=[
                    datetime.date.fromisoformat("1990-02-03")
                    for _ in range(num_of_travelers)
                ],
                session_token="YMSXrOAhIOdvIbxAmfSt7vJtRBkurNb6",  # noqa: S106
            )
            for trip in trips["data"]
        ),
    )
    await asyncio.sleep(5)
    for offers_search in offers_searches:
        offers = json_api_doc.deserialize(
            await junction_client.get_offers_by_offer_search_id(
                offers_search["data"]["id"],
                limit=1,
                cabin_class=None,
                include=["groups.options", "groups.details"],
            ),
        )
        if offers:
            break
    else:
        raise RuntimeError("Couldn't find offers")
    # Mypy bug: https://github.com/python/mypy/issues/14209
    offer_group = offers[0]["groups"][0]  # type: ignore[possibly-undefined]
    offer_group_details = offer_group["details"][0]
    offer_group_options = offer_group["options"]
    try:
        short_link = await shorten_link(
            origin,
            destination,
            departure_at,
            num_of_travelers,
        )
    except exceptions.HTTPException:
        short_link = "phoenix.junction.dev/"
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
            + "\nBook it here: {0}".format(short_link)
        ),
        receiver=receiver_mobile,
    )


async def shorten_link(
    origin: str,
    destination: str,
    date: str,
    num_of_passengers: int,
) -> str:
    original_link = "https://phoenix.sandbox.junction.dev/book?type=oneway&adults={0}&children=0&infants=0&originId={1}&destinationId={2}&departureDate={3}".format(
        num_of_passengers,
        origin,
        destination,
        date,
    )
    async with httpx.AsyncClient() as link_client:
        response = await link_client.post(
            "https://api.short.io/links",
            headers={
                "accept": "application/json",
                "content-type": "application/json",
                "Authorization": "sk_NVVkt7ci4TIVmxOp",
            },
            json={
                "domain": "ahm0.short.gy",
                "originalURL": original_link,
            },
        )
        return response.json()["shortURL"]
