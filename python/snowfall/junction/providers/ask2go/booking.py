import asyncio
import datetime

import phonenumbers
import pycountry
import structlog

from snowfall.junction.orders.v1alpha import models_pb2
from snowfall.junction.providers.ask2go import criteria, models, notifications
from snowfall.stdlib.format import protobuf
from snowfall.vendor.ask2go import client, errors
from snowfall.vendor.ask2go.models import booking, common


class BookingHandler(object):
    _poll_retries_limit = 10
    _wait_time_between_polling = 1

    def __init__(
        self,
        ask2go_client: client.Ask2GoClient,
        notifier: notifications.Notifier,
    ):
        self._client = ask2go_client
        self._logger = structlog.get_logger(__name__)
        self._notifier = notifier

    async def book(
        self,
        order: models_pb2.Order,
        offer_id: str,
        details: tuple[str, str],
    ) -> booking.Booking:
        number = phonenumbers.parse(order.contact_details.phone.e164_number)
        country = pycountry.countries.get(
            alpha_2=order.contact_details.address.region_code,
        )

        booking_result = await self._client.create_booking(
            pricing_id=details[0],
            transaction_id=details[1],
            passengers=[
                common.Passenger(
                    first_name=passenger.first_name,
                    last_name=passenger.last_name,
                    name_title=models_pb2.Passenger.Title.Name(passenger.title),
                    gender=models.gender_from_proto(passenger.gender),
                    type=criteria.get_passenger_type(
                        protobuf.protobuf_to_date(passenger.date_of_birth),
                        datetime.date.today(),  # todo: date of travel
                    ),
                    birth_date=protobuf.protobuf_to_date(passenger.date_of_birth),
                )
                for passenger in order.passengers
            ],
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
            ),
        )

        await self._client.update_booking_billing_address(
            booking_ref_id=booking_result.id,
            transaction_id=booking_result.transaction_id,
        )
        booking_result = await self._poll_booking(booking_result)

        try:
            # todo: this should be handled in a separate service
            await self._notifier.send(
                notifications.BookingNotification(order, booking_result),
            )
        except notifications.NotificationError:
            self._logger.exception()

        return booking_result

    async def _poll_booking(self, model: booking.Booking) -> booking.Booking:
        for _ in range(self._poll_retries_limit):
            model = await self._client.get_booking(
                booking_ref_id=model.id,
                transaction_id=model.transaction_id,
            )

            if model.contact_details:
                return model

            await asyncio.sleep(self._wait_time_between_polling)

        raise errors.ServiceError("Unable to get booking details in time")
