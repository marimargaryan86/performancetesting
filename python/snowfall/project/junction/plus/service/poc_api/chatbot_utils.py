import asyncio
import datetime
from typing import Any, Mapping, Sequence

import httpx
import json_api_doc

from snowfall.project.junction.plus.service.poc_api import (
    flight_stats_client,
    repository,
    twilio,
)
from snowfall.vendor.junction.go import client

_ORDER_STATUS_POLLING_TIMEOUT = 180
_ORDER_STATUS_POLLING_INTERVAL = 10
_SUCCESS_STATUSES = frozenset(
    (
        "confirmed",
        "not-ticketed",
    ),
)
_VENDOR = "vendor"
_ROUTE_IDENTIFIERS = "routeIdentifiers"


def order_details_by_date(
    details: Sequence[Mapping[str, Any]],
    delay_obj: Mapping[str, Any],
) -> Sequence[Mapping[str, Any]]:
    ordered_details = [
        {
            "origin": leg["origin"],
            "destination": leg["destination"],
            "departureAt": leg["departureAt"],
            "arrivalAt": leg["arrivalAt"],
            "ref": {
                "carrier": segment["vendor"],
                "flight": segment["routeIdentifiers"]["vendor"],
            },
            "legType": segment["legType"]["id"],
            "durationSeconds": (
                datetime.datetime.fromisoformat(
                    leg["arrivalAt"],
                )
                - datetime.datetime.fromisoformat(
                    leg["departureAt"],
                )
            ).seconds,
            "delayMinutes": (
                delay_obj[segment["vendor"] + segment["routeIdentifiers"]["vendor"]]
                if segment["vendor"] + segment["routeIdentifiers"]["vendor"]
                in delay_obj
                else 0
            ),
        }
        for segment in details
        for leg in segment["legs"]
    ]
    ordered_details.sort(
        key=lambda leg: datetime.datetime.fromisoformat(leg["departureAt"]),
    )
    return ordered_details


async def build_travel_essential(  # noqa: WPS210
    order: Mapping[str, Any],
    delay_webhook_repository: repository.DelayWebhookRepository,
    fs_client: flight_stats_client.FlightStatusClient,
) -> str:
    delays = await delay_webhook_repository.search_by_order(order["id"])
    delay_obj = {
        delay["flight_key"]: sum(
            history["delay_minutes"] for history in delay.get("delay_history", [])
        )
        async for delay in delays
    }
    details = order_details_by_date(
        [detail for booking in order["bookings"] for detail in booking["details"]],
        delay_obj,
    )
    signature = journey_signature(order)
    total_seconds = sum(detail["durationSeconds"] for detail in details)
    tem = (
        "Here are the details of your upcoming trip\n"
        + "From {0} to {1}\n".format(signature["origin"], signature["destination"])
        + "Booking reference: {0}\n".format(signature["reference"])
        + "Duration: {0}h{1}m\n".format(
            seconds_to_hours_and_minutes(total_seconds)["hours"],
            seconds_to_hours_and_minutes(total_seconds)["minutes"],
        )
    )
    if len(details) > 1:
        tem += "Stops: {0}\n".format(len(details))
    else:
        tem += "Non Stop\n"  # noqa: WPS336

    for detail in details:
        fs = await get_flight_status(detail, fs_client)
        delay_minutes = detail["delayMinutes"]
        departure_terminal = "[terminal], [gate]\n" if fs else ""
        arrival_terminal = "[terminal]\n" if fs else ""
        leg_tem = (
            "----------------------\n"
            + "Departure from: {0}\n".format(detail["origin"]["name"])
            + departure_terminal
            + "Departure time: {0}\n".format(format_dt_str(detail["departureAt"]))
            + (
                "Delayed: by +{0}m, {1}\n".format(  # noqa: WPS509
                    delay_minutes,
                    format_dt(
                        datetime.datetime.fromisoformat(
                            detail["departureAt"],
                        )
                        + datetime.timedelta(
                            minutes=delay_minutes,
                        ),
                    ),
                )
                if delay_minutes
                else ""
            )
            + "Arrival to: {0}\n".format(detail["destination"]["name"])
            + arrival_terminal
            + "Arrival time: {0}\n".format(format_dt_str(detail["arrivalAt"]))
            + (
                "Delayed: by +{0}m, {1}\n".format(  # noqa: WPS509
                    delay_minutes,
                    format_dt(
                        datetime.datetime.fromisoformat(
                            detail["arrivalAt"],
                        )
                        + datetime.timedelta(
                            minutes=delay_minutes,
                        ),
                    ),
                )
                if delay_minutes
                else ""
            )
            + "Duration: {0}h{1}m\n".format(
                seconds_to_hours_and_minutes(detail["durationSeconds"])["hours"],
                seconds_to_hours_and_minutes(detail["durationSeconds"])["minutes"],
            )
            + "Mode of transport: {0}\n".format(detail["legType"])
            + "Airline: [Operator]\n"
            + "Flight number: {0}\n".format(
                detail["ref"]["carrier"] + detail["ref"]["flight"],
            )
        )
        tem += leg_tem
    return tem


def seconds_to_hours_and_minutes(seconds: int) -> Mapping[str, int]:
    (hours, remaining) = divmod(seconds, 3600)  # noqa: WPS432
    (minutes, _) = divmod(remaining, 60)
    return {"hours": hours, "minutes": minutes}


async def get_flight_status(
    detail: Mapping[str, Any],
    fs_client: flight_stats_client.FlightStatusClient,
) -> str:
    try:
        status = await fs_client.get_flight_status(
            datetime.datetime.fromisoformat(detail["departureAt"]),
            detail["ref"]["carrier"],
            detail["ref"]["flight"],
        )
    except httpx.HTTPStatusError:
        return ""
    if "flightStatuses" not in status:
        return ""
    return "\nAirport Resources\n" + "\n".join(  # noqa: WPS336
        "{0}: {1}".format(_key, resource)
        for _key, resource in status["flightStatuses"][0]["airportResources"].items()
    )


def home_message() -> str:
    return "Available commands: \nTravel status"


def journey_signature(doc: Mapping[str, Any], idx: int = 0) -> Mapping[str, Any]:
    origin_leg = doc["bookings"][0]["details"][0]["legs"][0]  # noqa: WPS221, WPS219
    dest_leg = doc["bookings"][-1]["details"][-1]["legs"][-1]  # noqa: WPS221, WPS219
    destination = dest_leg["destination"]
    return {
        "idx": idx + 1,
        "reference": doc["journey"]["reference"],
        "origin": origin_leg["origin"]["name"],
        "destination": destination["name"],
        "departure_at": format_dt_str(origin_leg["departureAt"]),
        "arrival_at": format_dt_str(dest_leg["arrivalAt"]),
    }


def journey_signature_str(
    doc: Mapping[str, Any],
    idx: int = 0,
) -> str:
    signature = journey_signature(doc, idx)
    return "{0}) {1}: {2} to {3} - {4}".format(
        signature["idx"],
        signature["reference"],
        signature["origin"],
        signature["destination"],
        signature["departure_at"],
    )


def filter_future_orders(
    docs: Sequence[Mapping[str, Any]],
) -> Sequence[Mapping[str, Any]]:
    return [
        doc
        for doc in docs
        if datetime.datetime.fromisoformat(
            doc["bookings"][0]["details"][0]["legs"][0][  # noqa: WPS219 EXTRA COM
                "departureAt"
            ],
        ).replace(tzinfo=None)
        > datetime.datetime.now()
    ]


async def register_booking_confirmation_agent(
    junction_client: client.Client,
    twilio_client: twilio.TwilioClient,
    order_id: str,
    mobile: str,
    delay_webhook_repository: repository.DelayWebhookRepository,
) -> None:
    order = await poll_order_status(
        junction_client,
        order_id,
        delay_webhook_repository,
    )
    if order:
        reference = order["journey"]["reference"]
        signature = journey_signature(order)
        twilio_client.send_message(
            body=(
                "We are pleased to confirm that your trip from "
                + "{0} to {1} on {2} is booked!".format(
                    signature["origin"],
                    signature["destination"],
                    signature["departure_at"],
                )
                + "\nBooking Reference: {0}".format(signature["reference"])
                + "\nFor more info, reply TRAVEL STATUS"
            ),
            receiver=mobile,
        )
        if check_auto_checkin_availability():
            twilio_client.send_message(
                body=(
                    "Automatic Checkin is available for your booking with "
                    + "reference: {0}.".format(reference)
                    + " If you want to proceed with automatic checkin, reply: CHECKIN"
                ),
                receiver=mobile,
            )
    else:
        twilio_client.send_message(
            body="Something went wrong with order creation",
            receiver=mobile,
        )


def check_auto_checkin_availability() -> bool:
    return False


async def poll_order_status(
    junction_client: client.Client,
    order_id: str,
    delay_webhook_repository: repository.DelayWebhookRepository,
) -> Mapping[str, Any] | None:
    time_spent = 0
    while time_spent <= _ORDER_STATUS_POLLING_TIMEOUT:
        order = json_api_doc.deserialize(
            await junction_client.get_order_by_id(
                identifier=order_id,
                include=["journey", "bookings.details"],
            ),
        )
        booking_statuses = {booking["status"]["id"] for booking in order["bookings"]}
        if booking_statuses and not booking_statuses.difference(_SUCCESS_STATUSES):
            await add_delay_webhook(order, delay_webhook_repository)
            return order
        if "pending" not in booking_statuses:
            return None
        await asyncio.sleep(_ORDER_STATUS_POLLING_INTERVAL)
        time_spent += _ORDER_STATUS_POLLING_INTERVAL

    return None


async def send_subscription(
    twilio_client: twilio.TwilioClient,
    mobile: str,
) -> None:
    twilio_client.send_message(
        body="Thank you for your booking. "
        + "Would you like to receive travel related updates via WhatsApp?",
        receiver=mobile,
    )


async def add_delay_webhook(
    order: Mapping[str, Any],
    delay_webhook_repository: repository.DelayWebhookRepository,
) -> None:
    for booking in order["bookings"]:
        for detail in booking["details"]:
            await delay_webhook_repository.add_order(
                flight_key=detail["vendor"] + detail["routeIdentifiers"]["vendor"],
                flight_details={
                    "origin": detail["legs"][0]["origin"],
                    "destination": detail["legs"][0]["destination"],
                    "departure_at": detail["legs"][0]["departureAt"],
                },
                order_id=order["id"],
            )


async def send_delay(
    order: Mapping[str, Any],
    delay_webhook: Mapping[str, Any],
    delay: int,
    twilio_client: twilio.TwilioClient,
) -> None:
    new_departure = datetime.datetime.fromisoformat(
        delay_webhook["flight_details"]["departure_at"],
    ) + datetime.timedelta(minutes=delay)
    for old_delay in delay_webhook.get("delay_history", []):
        new_departure = new_departure + datetime.timedelta(
            minutes=old_delay["delay_minutes"],
        )
    twilio_client.send_message(
        body=(
            "Delay for your travel of {0} minutes.".format(delay)
            + "\nFROM {0} TO {1}. ".format(
                delay_webhook["flight_details"]["origin"]["name"],
                delay_webhook["flight_details"]["destination"]["name"],
            )
            + "\nOriginal departure time: {0}".format(
                format_dt_str(
                    delay_webhook["flight_details"]["departure_at"],
                ),
            )
            + "\nNew estimated departure time: {0}".format(format_dt(new_departure))
        ),
        receiver="".join(order["journey"]["contactDetails"]["phoneNumber"].split()),
    )


def format_dt(dt: datetime.datetime) -> str:
    return dt.strftime(
        "%A %d %b %Y %H:%M",
    )


def format_dt_str(dt: str) -> str:
    return datetime.datetime.fromisoformat(dt).strftime(
        "%A %d %b %Y %H:%M",
    )
