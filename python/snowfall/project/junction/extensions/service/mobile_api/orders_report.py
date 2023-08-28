import contextlib
import csv
import datetime
import io
from collections.abc import Mapping, Sequence

import aiosmtplib
import httpx
import json_api_doc
from authlib.integrations import httpx_client
from dateutil import relativedelta
from motor import motor_asyncio
from pydantic import AnyUrl, HttpUrl

from snowfall.project.junction.extensions.service.mobile_api import smtp
from snowfall.project.junction.extensions.service.mobile_api.tasks import orders
from snowfall.stdlib import service
from snowfall.stdlib.integration.starlette import application
from snowfall.stdlib.transport.http import auth
from snowfall.vendor.junction.go import client


class Settings(application.Settings):
    smtp_dsn: AnyUrl
    mongo_dsn: Sequence[AnyUrl]
    orders_report_email: str
    junction_api_address: str
    ory_client_token_endpoint: HttpUrl
    ory_client_id: str
    ory_client_secret: str


async def orders_report(app: service.Application[Settings]) -> None:
    mongo = motor_asyncio.AsyncIOMotorClient(
        app.settings.mongo_dsn,
    )[app.name]
    junction_client = client.Client(
        base_url=app.settings.junction_api_address,
        auth=auth.ClientCredentialsAuth(
            client=httpx_client.AsyncOAuth2Client(
                client_id=app.settings.ory_client_id,
                client_secret=app.settings.ory_client_secret,
            ),
            token_endpoint=str(app.settings.ory_client_token_endpoint),
        ),
    )
    smtp_cl = smtp.EmailClient(
        aiosmtplib.SMTP(
            hostname=app.settings.smtp_dsn.host,
            port=int(app.settings.smtp_dsn.port or 0) or None,
            username=app.settings.smtp_dsn.username,
            password=app.settings.smtp_dsn.password,
            start_tls=False,
        ),
        client_name="",
        support_email="",
    )

    await _send_report(
        await _generate_report(
            mongo["orders"],
            junction_client,
        ),
        smtp_cl,
        app.settings.orders_report_email,
    )


async def _generate_report(  # noqa: WPS210
    orders_repository: motor_asyncio.AsyncIOMotorCollection,
    junction_client: client.Client,
) -> Sequence[Mapping[str, str | int | float]]:
    junction_orders = []
    mobile_orders = orders_repository.find(
        {
            "created_at": {
                "$gt": datetime.datetime.now(
                    tz=datetime.UTC,
                ) - relativedelta.relativedelta(months=1),
            },
        },
    )
    async for mobile_order in mobile_orders:
        with contextlib.suppress(httpx.HTTPStatusError):
            junction_orders.append(
                json_api_doc.deserialize(
                    await junction_client.get_order_by_id(
                        mobile_order["_id"],
                        include=[
                            "journey",
                            "bookings",
                            "bookings.details",
                        ],
                    ),
                ),
            )
    ret = []
    for order in junction_orders:
        bookings = order["bookings"]
        ret.append(
            {
                "passengers": order["passengers"],
                "contactDetails": order["journey"]["contactDetails"],
                "totalPrice": sum(
                    [float(booking["totalPrice"]["amount"]) for booking in bookings],
                ),
                "currency": bookings[0]["totalPrice"]["currency"],
                "operatorBookingReferences": [
                    reference
                    for booking in bookings
                    for reference in booking["operatorBookingReferences"]
                ],
                "status": (
                    "failed"
                    if {booking["status"]["id"] for booking in bookings}.difference(
                        orders._SUCCESS_STATUSES,  # noqa: SLF001
                    )
                    else "success"
                ),
                "segments": [
                    {
                        field: detail[field]
                        for field in (
                            "cabinClassName",
                            "vendor",
                            "operator",
                            "routeIdentifiers",
                            "legs",
                        )
                    }
                    for booking in bookings
                    for detail in booking["details"]
                ],
            },
        )
    return ret


async def _send_report(
    rows: Sequence[Mapping[str, str | int | float]],
    smtp_cl: smtp.EmailClient,
    email: str,
) -> None:
    csv_file = io.StringIO()
    dict_writer = csv.DictWriter(
        csv_file,
        fieldnames=rows[0].keys(),
    )
    dict_writer.writeheader()
    dict_writer.writerows(rows)
    await smtp_cl.send_email_notification(
        email,
        "Monthly orders report",
        "Monthly orders report",
        smtp.Attachment(
            payload=csv_file.getvalue(),
            main_type="text",
            sub_type="csv",
            file_name="orders.csv",
        ),
    )
