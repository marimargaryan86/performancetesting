import asyncio
import base64
import tempfile
import time
import urllib
from collections.abc import (
    AsyncGenerator,
    Mapping,
    Sequence,
)
from datetime import date, datetime
from io import BytesIO
from typing import Any

import boto3
import httpx
import pandas as pd
import stripe
from hvac import Client, exceptions
from pymongo import MongoClient

from snowfall.project.junction.api_automation.test_functions.mobile_client import (
    MobileApiClient,
)


async def wait_until_completed(
    request_func: Any,
    error_message: str,
    max_wait_time_seconds: int = 120,
    polling_interval: int = 5,
) -> Any:
    stopwatch = time.time() + max_wait_time_seconds

    while stopwatch - time.time() > 0:
        response = await request_func()
        if response["attributes"]["status"] == "completed":
            return response
        await asyncio.sleep(polling_interval)

    raise AssertionError(error_message)


async def wait_for_response(
    request_func: Any,
    error_message: str,
    max_wait_time_seconds: int = 120,
    polling_interval: int = 10,
) -> Any:
    stopwatch = time.time() + max_wait_time_seconds

    while stopwatch - time.time() > 0:
        response = await request_func()
        if response["data"]:
            return response
        await asyncio.sleep(polling_interval)

    raise AssertionError(error_message)


def connect_to_aws() -> Any:
    aws_access_key_id = "AKIA6JO5TGEWJNIU4LNR"
    aws_secret_access_key = "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"  # noqa: S105
    bucket_name = "junctionqa"
    file_key = "rails_origin_destination.csv"

    s3 = boto3.client(
        "s3",
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
    )
    response = s3.get_object(Bucket=bucket_name, Key=file_key)
    return response["Body"].read()


def get_places() -> list[tuple[str, str]]:
    data = connect_to_aws()
    o_d_combination = pd.read_csv(BytesIO(data), sep=";")
    origin_values = o_d_combination["Origin"].tolist()
    destination_values = o_d_combination["Destination"].tolist()
    return list(zip(origin_values, destination_values, strict=False))


async def get_coordinates_by_place_name(
    mongo_client: MongoClient[Any],
    place_pairs: Sequence[tuple[Any, Any]],
) -> list[tuple[Any, Any]]:
    place_id_pairs = []
    for place in place_pairs:
        place_result = mongo_client["places"]["places"].find_one(
            filter={"location.name": place},
        )
        coordinate0, coordinate1 = None, None
        if place_result is not None:
            coordinates = place_result.get("location")
            if coordinates is not None:
                coordinate0, coordinate1 = coordinates.get("coordinates").get(
                    "coordinates",
                )
        place_id_pairs.append((coordinate1, coordinate0))

    return place_id_pairs


async def stripe_confirmation(
    payment_intent_id: str,
    stripe_api_key: str,
) -> dict[str, str]:
    payment_method = stripe.PaymentMethod.create(
        api_key=stripe_api_key,
        type="card",
        card={
            "number": "4242424242424242",
            "exp_month": 12,
            "exp_year": 2034,
            "cvc": "314",
        },
    )
    stripe.PaymentIntent.modify(
        payment_intent_id,
        api_key=stripe_api_key,
        payment_method=payment_method["id"],
    )
    stripe.PaymentIntent.confirm(
        payment_intent_id,
        api_key=stripe_api_key,
        return_url="https://example.com/return_url",
    )
    return stripe.PaymentIntent.retrieve(
        payment_intent_id,
        api_key=stripe_api_key,
    )


def get_variable_value(
    host: str,
    api_token: str,
    variable_name: str,
) -> str:
    vusername, vpassword = api_token.split("+")
    client = Client(url=host)
    client.auth.userpass.login(username=vusername, password=vpassword)
    is_authenticated = client.is_authenticated()
    returned_data = {}
    if is_authenticated:
        returned_data = get_variable_from_server(client, "sandbox")
        if not returned_data:
            returned_data = get_variable_from_server(client, "development")
            if not returned_data:
                returned_data = get_variable_from_server(client, "production")

    return str(returned_data["data"]["data"][variable_name])


def get_variable_from_server(
    client: Client,
    environment: str,
) -> dict[str, Any]:
    query = "kv/data/{e}/{s}".format(e=environment, s="api-automation")
    try:
        returned_data = client.read(query)
    except exceptions.Forbidden:
        returned_data = {}

    if not isinstance(returned_data, dict):
        raise TypeError

    return returned_data


class ConfigurationManager:
    def __init__(self, host: str, api_token: str) -> None:
        self.host = host
        self.api_token = api_token

    def get_br_cert(self) -> str:
        br_base64_cert = get_variable_value(self.host, self.api_token, "br_base64_cert")
        return str(br_base64_cert)

    def get_br_api_host(self) -> str:
        br_api_host = get_variable_value(self.host, self.api_token, "br_api_host")
        return str(br_api_host)

    def get_br_subscription_key(self) -> str:
        br_subscription_key = get_variable_value(
            self.host,
            self.api_token,
            "br_subscription_key",
        )
        return str(br_subscription_key)


async def create_br_connection(
    config_manager: ConfigurationManager,
) -> AsyncGenerator[httpx.AsyncClient, None]:
    cert = (config_manager.get_br_cert(),)
    base64_cert = "-----BEGIN CERTIFICATE-----\n{0}\n-----END CERTIFICATE-----".format(
        cert[0],
    )
    decoded_cert = base64.b64decode(urllib.parse.unquote(base64_cert))

    with tempfile.NamedTemporaryFile(delete=False) as temp_cert_file:
        temp_cert_file.write(decoded_cert)
        temp_cert_file_name = temp_cert_file.name
    async with httpx.AsyncClient(http2=True, cert=temp_cert_file_name) as client:
        yield client


async def make_br_request(
    config_manager: ConfigurationManager,
    method: str,
    endpoint: str,
    payload: Mapping[str, Any],
    custom_headers: Mapping[str, Any] | None = None,
) -> tuple[dict[str, Any], Any]:
    base_url = config_manager.get_br_api_host()
    subscription_key = config_manager.get_br_subscription_key()
    full_url = urllib.parse.urljoin(base_url, endpoint)

    default_headers = {
        "Cache-Control": "no-cache",
        "Ocp-Apim-Subscription-Key": subscription_key,
        "Content-Type": "application/json",
        "x-bnds-user-token": "ea44f55b-f390-4327-b3a7-9d79668d4f11",
    }
    headers = default_headers
    if custom_headers is not None:
        headers = {**default_headers, **custom_headers}
    async for conn in create_br_connection(config_manager):
        response = await conn.request(
            method,
            full_url,
            json=payload,
            headers=headers,
        )
        response.raise_for_status()
        response_hearder = response.headers
        response_data = response.json()

        return response_data, response_hearder
    raise RuntimeError("Error on Benerail requests")


async def get_place_coordinates(
    mobile_client: MobileApiClient,
    place_pairs: Sequence[str],
) -> list[tuple[Any, Any]]:
    place_id_pairs = []
    for place in place_pairs:
        response = await mobile_client.get_places(place)
        latitude = response["data"][0]["attributes"]["latitude"]
        longitude = response["data"][0]["attributes"]["longitude"]
        place_id_pairs.append((latitude, longitude))
    return place_id_pairs


async def create_offer_simple_search(
    mobile_hub_client: MobileApiClient,
    departure_after: datetime,
    departure_before: datetime,
    origin: tuple[float, float],
    destination: tuple[float, float],
    passengers_dates_of_birth: Sequence[date],
    maximum_connections: Any,
    allowed_segment_types: Any,
) -> dict[str, Any]:
    return await mobile_hub_client.create_offer_simple_search(
        origin,
        destination,
        departure_after,
        departure_before,
        passengers_dates_of_birth,
        maximum_connections,
        allowed_segment_types,
    )


async def get_search_offers(
    mobile_client: MobileApiClient,
    simple_offer_searches_id: str,
) -> Any:
    offers_searches = await mobile_client.get_offer_search(simple_offer_searches_id)
    return offers_searches["data"]


async def get_offer_list_simple_search(
    mobile_hub_client: MobileApiClient,
    offer_id_simple_search: str,
) -> dict[str, Any]:
    return await mobile_hub_client.list_offers_simple_search(
        offer_simple_search_id=offer_id_simple_search,
    )


async def get_option_id(  # noqa: WPS231
    offer_id: str,
    offer_list: Mapping[str, Any],
) -> str:
    option_id = ""
    offer_group_id = ""
    offer_data = offer_list["data"][0]
    offer_list_included = offer_list["included"]

    if offer_data["id"] == offer_id:
        offer_groups = offer_data["relationships"]["groups"]
        offer_group_id = offer_groups["data"][0]["id"]

    for offer_item in offer_list_included:
        if offer_item.get("id") == offer_group_id:
            options = offer_item.get("relationships", {}).get("options", [])
            option_id = options["data"][0]["id"]

    return option_id


async def create_quote(
    mobile_client: MobileApiClient,
    offer_id: str,
    option_ids: Sequence[str],
) -> str:
    quote = await mobile_client.create_offer_price_quote(
        offer_id=offer_id,
        option_ids=option_ids,
    )
    return quote["data"]["id"]


async def create_payment(
    mobile_client: MobileApiClient,
    currency: str,
    amount: str,
) -> str:
    quote = await mobile_client.create_payment(
        currency=currency,
        amount=amount,
    )
    return quote["data"]["id"]


async def get_quote(
    mobile_client: MobileApiClient,
    quote: str,
) -> Mapping[str, Any]:
    get_quotes = await mobile_client.get_offer_price_quote(
        offer_price_quote_id=quote,
    )
    return get_quotes["data"]


async def create_order(
    mobile_client: MobileApiClient,
    trip_offer_price_quotes: str,
    payment_id: str,
) -> Mapping[str, Any]:
    year = 1980
    month = 2
    day = 3
    passenger_date_of_birth = [date(year, month, day)]

    order = await mobile_client.create_order_with_payment(
        passenger_date_of_birth,
        trip_offer_price_quotes,
        payment_id,
    )
    return order["data"]
