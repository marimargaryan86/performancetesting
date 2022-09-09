import json

import httpx

from snowfall.vendor.direct_ferries.clients import base
from snowfall.vendor.direct_ferries.models import booking

_DATA_KEY = "data"


class BookingClient(base.BaseClient):
    async def confirm_booking(
        self,
        booking_id: int,
        booking_token: str,
    ) -> booking.BookingResponse:
        response_data = (
            await self._make_request(
                request_details=base.RequestDetails(
                    url="{0}/api/{1}/Bookings/confirm-booking-request".format(
                        self._config.api_url,
                        self._config.api_version,
                    ),
                    method="post",
                    payload=json.dumps(
                        {
                            "bookingId": booking_id,
                            "bookingToken": booking_token,
                        },
                    ),
                ),
            )
        ).json()

        return booking.BookingResponse(**response_data[_DATA_KEY])

    async def retrieve(self, booking_id: int) -> booking.BookingResponse:
        response_data = (
            await self._make_request(
                request_details=base.RequestDetails(
                    url="{0}/api/{1}/Bookings/{2}/retrieve".format(
                        self._config.api_url,
                        self._config.api_version,
                        str(booking_id),
                    ),
                    method="get",
                ),
            )
        ).json()

        return booking.BookingResponse(**response_data[_DATA_KEY])

    async def get_cancellation_enquiry(
        self,
        booking_id: int,
        booking_token: str,
    ) -> booking.CancellationEnquiryInformation:
        response_data = (
            await self._make_request(
                request_details=base.RequestDetails(
                    url="{0}/api/{1}/Bookings/{2}/cancellation-enquiry".format(
                        self._config.api_url,
                        self._config.api_version,
                        str(booking_id),
                    ),
                    method="get",
                    query_params=httpx.QueryParams(
                        PartnerCode=self._config.partner_code,
                        BookingToken=booking_token,
                    ),
                ),
            )
        ).json()

        return booking.CancellationEnquiryInformation(**response_data[_DATA_KEY])

    async def cancel_booking(
        self,
        booking_id: int,
        booking_token: str,
        refund_amount: str,
    ) -> booking.CancellationResponse:
        response_data = (
            await self._make_request(
                request_details=base.RequestDetails(
                    url="{0}/api/{1}/Bookings/{2}/cancel-booking".format(
                        self._config.api_url,
                        self._config.api_version,
                        str(booking_id),
                    ),
                    method="post",
                    payload=json.dumps(
                        {
                            "bookingId": booking_id,
                            "bookingToken": booking_token,
                            "refundAmount": refund_amount,
                            "cancellationReason": "Cancel",
                        },
                    ),
                ),
            )
        ).json()

        return booking.CancellationResponse(**response_data[_DATA_KEY])
