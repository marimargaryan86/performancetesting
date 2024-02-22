import pathlib
from email.mime import multipart, text

import aiofiles
import aiosmtplib
import jinja2

from snowfall.project.junction.go.service.orders.v1 import amqp_pb2
from snowfall.project.junction.service.providers.carnect import adapter
from snowfall.vendor.carnect.adapters import reservation_adapter


class EmailNotificationError(Exception):
    """General error while sending email notification."""


class BookingNotification(object):
    def __init__(
        self,
        place_order_task: amqp_pb2.PlaceOrderTask,
        res_adapter: reservation_adapter.ReservationAdapter,
        template: pathlib.Path,
    ):
        self._place_order_task = place_order_task
        self._res_adapter = res_adapter
        self._template = template

    @property
    def subject(self) -> str:
        return "CARNECT BOOKING : {identifier}".format(
            identifier=self._res_adapter.get_id_context(),
        )

    async def get_body(self) -> str:
        async with aiofiles.open(self._template) as template_file:
            template_content = await template_file.read()

        reservation = self._res_adapter.reservation()
        pickup_date = adapter.get_optional_value(
            reservation,
            "veh_segment_core.veh_rental_core.pick_up_date_time",
            "N/A",
        )
        drop_off_date = adapter.get_optional_value(
            reservation,
            "veh_segment_core.veh_rental_core.return_date_time",
            "N/A",
        )
        pick_up_location = adapter.get_optional_value(
            reservation,
            "veh_segment_core.veh_rental_core.pick_up_location",
            "N/A",
        )
        origin = pick_up_location[0].value if pick_up_location else "N/A"
        destination = adapter.get_optional_value(
            reservation,
            "veh_segment_core.veh_rental_core.return_location.value",
            "N/A",
        )
        operator = adapter.get_optional_value(
            reservation,
            "veh_segment_core.vendor.company_short_name",
            "N/A",
        )
        return jinja2.Template(template_content).render(
            spnr=self._place_order_task.metadata.passenger_name_record,
            pickup_date=pickup_date,
            drop_off_date=drop_off_date,
            origin=origin,
            destination=destination,
            journey_id=self._place_order_task.metadata.journey_id,
            passengers=self._place_order_task.passengers,
            operator_reference=self._res_adapter.get_id_context(),
            operator=operator,
        )


class EmailClient(object):
    def __init__(self, client: aiosmtplib.SMTP, sender: str):
        self._smtp = client
        self._sender = sender

    async def send_email_html_template(
        self,
        mail_to: str,
        subject: str,
        body: str,
    ) -> None:
        email = multipart.MIMEMultipart("alternative")
        email["From"] = self._sender
        email["To"] = mail_to
        email["Subject"] = subject
        email.attach(text.MIMEText(body, "html", "utf-8"))

        try:
            async with self._smtp:
                await self._smtp.send_message(email)
        except (ValueError, aiosmtplib.errors.SMTPException) as error:
            raise EmailNotificationError from error
