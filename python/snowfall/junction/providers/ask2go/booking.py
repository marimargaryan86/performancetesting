import datetime
from email import message

import aiosmtplib
import phonenumbers
import pycountry
import rapidjson
import structlog

from snowfall.junction.orders.v1alpha import models_pb2
from snowfall.junction.providers.ask2go import criteria
from snowfall.stdlib.format import protobuf
from snowfall.vendor.ask2go import client
from snowfall.vendor.ask2go.models import booking, common


class BookingHandler(object):
    def __init__(
        self,
        a2g_client: client.Ask2GoClient,
        smtp_client: aiosmtplib.SMTP,
    ):
        self._client = a2g_client
        self._logger = structlog.get_logger(__name__)
        self._smtp = smtp_client

    async def book(
        self,
        order: models_pb2.Order,
        offer_id: str,
        details: tuple[str, str],
    ) -> booking.Booking:
        # todo: handle multiple passengers when client does
        passenger = order.passengers[0]
        gender = common.Gender.unknown

        if passenger.gender == models_pb2.Passenger.GENDER_MALE:
            gender = common.Gender.male
        elif passenger.gender == models_pb2.Passenger.GENDER_FEMALE:
            gender = common.Gender.female

        number = phonenumbers.parse(order.contact_details.phone.e164_number)
        country = pycountry.countries.get(
            alpha_2=order.contact_details.address.region_code,
        )

        booking_result = await self._client.create_booking(
            pricing_id=details[0],
            transaction_id=details[1],
            passenger=common.Passenger(
                first_name=passenger.first_name,
                last_name=passenger.last_name,
                name_title=models_pb2.Passenger.Title.Name(passenger.title),
                gender=gender,
                type=criteria.get_passenger_type(
                    protobuf.protobuf_to_date(passenger.date_of_birth),
                    datetime.date.today(),  # todo: date of travel
                ),
                birth_date=protobuf.protobuf_to_date(passenger.date_of_birth),
            ),
            contact=common.Contact(
                address="\n".join(order.contact_details.address.address_lines),
                city=order.contact_details.address.locality,
                postal_code=order.contact_details.address.postal_code,
                country=common.Country(
                    code=country.alpha_2,
                    name=country.name,
                ),
                phone=common.Phone(
                    country_code=str(number.country_code),
                    number=str(number.national_number),
                ),
                email=order.contact_details.email,
                first_name=passenger.first_name,
                last_name=passenger.last_name,
                title=models_pb2.Passenger.Title.Name(passenger.title),
            ),
        )

        try:
            await self._send_email_notification(order, offer_id, booking_result)
        except Exception:  # noqa: PIE786
            self._logger.exception()

        return booking_result

    # todo: this should be handled in a separate service
    async def _send_email_notification(
        self,
        order: models_pb2.Order,
        offer_id: str,
        raw_data: booking.Booking,
    ) -> None:
        email = message.EmailMessage()
        email["From"] = "noreply@junction.travel"
        email["To"] = "A2GBooking@snowfalltravel.com"
        email["Subject"] = "A2G Booking in Junction needs ticketing!"
        email.set_content(
            "Order ID: {order} ({spnr}) Offer ID: {offer} Booking:\n{json}".format(
                order=order.id,
                spnr=order.passenger_name_record,
                offer=offer_id,
                json=rapidjson.dumps(
                    raw_data.dict(),
                    indent=2,
                    sort_keys=True,
                    number_mode=rapidjson.NM_NATIVE
                    | rapidjson.NM_DECIMAL
                    | rapidjson.NM_NAN,
                ),
            ),
        )

        async with self._smtp:
            await self._smtp.send_message(email)
