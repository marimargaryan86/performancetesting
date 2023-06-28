import http

from snowfall.stdlib.transport.http import client
from snowfall.vendor.benerail.clients import base
from snowfall.vendor.benerail.models.bookings import offer, order, payment
from snowfall.vendor.benerail.models.bookings import response as booking_response
from snowfall.vendor.benerail.models.products import response as product_response

_BASE_PATH = "/bookings/bookings"


class BookingsClient(base.BenerailBaseClient):  # noqa: WPS214
    async def create_booking(
        self,
        dialogue_id: str,
        etag: str,
    ) -> booking_response.GetBookingResponse:
        response = await self._make_request(
            client.RequestOptions(
                method="POST",
                path="{dialogue_prefix}/{dialogue_id}/booking".format(
                    dialogue_prefix=_BASE_PATH,
                    dialogue_id=dialogue_id,
                ),
                headers=self._get_headers(etag),
            ),
        )

        return booking_response.GetBookingResponse(**response.json())

    async def get_booking(
        self,
        booking_id: str,
    ) -> booking_response.GetBookingResponse:
        response = await self._make_request(
            client.RequestOptions(
                method="GET",
                path="{base_path}/{booking_id}".format(  # noqa: WPS204
                    base_path=_BASE_PATH,
                    booking_id=booking_id,
                ),
                headers=self._get_headers(),
            ),
        )

        return booking_response.GetBookingResponse(**response.json())

    async def create_order(
        self,
        booking_id: str,
        etag: str,
    ) -> booking_response.GetOrderResponse:
        response = await self._make_request(
            client.RequestOptions(
                method="POST",
                path="{base_path}/{booking_id}/orders".format(
                    base_path=_BASE_PATH,
                    booking_id=booking_id,
                ),
                headers=self._get_headers(etag),
            ),
        )

        return booking_response.GetOrderResponse(**response.json())

    async def booking_products(
        self,
        booking_id: str,
        order_id: str,
        booked_offer_id: str,
        tariff_ref: str,
    ) -> product_response.GetProductResponse:
        response = await self._make_request(
            client.RequestOptions(
                method="GET",
                path="".join(
                    [
                        "{base_path}/{booking_id}".format(
                            base_path=_BASE_PATH,
                            booking_id=booking_id,
                        ),
                        "/orders/{order_id}".format(order_id=order_id),  # noqa: WPS204
                        "/booked-offers/{booked_offer_id}".format(
                            booked_offer_id=booked_offer_id,
                        ),
                        "/products/{tariff_ref}".format(tariff_ref=tariff_ref),
                    ],
                ),
                headers=self._get_headers(),
            ),
        )

        return product_response.GetProductResponse(**response.json())

    async def get_booked_offer(
        self,
        booking_id: str,
        order_id: str,
        booked_offer_id: str,
    ) -> booking_response.GetBookedOfferResponse:
        response = await self._make_request(
            client.RequestOptions(
                method="GET",
                path="".join(
                    [
                        "{base_path}/{booking_id}".format(
                            base_path=_BASE_PATH,
                            booking_id=booking_id,
                        ),
                        "/orders/{order_id}".format(order_id=order_id),
                        "/booked-offers/{booked_offer_id}".format(
                            booked_offer_id=booked_offer_id,
                        ),
                    ],
                ),
                headers=self._get_headers(),
            ),
        )
        return booking_response.GetBookedOfferResponse(**response.json())

    async def get_booked_offer_parts(
        self,
        booking_id: str,
        order_id: str,
        booked_offer_id: str,
        booked_offer_part_id: str,
    ) -> booking_response.GetBookedOfferPartResponse:
        response = await self._make_request(
            client.RequestOptions(
                method="GET",
                path="".join(
                    [
                        "{base_path}/{booking_id}".format(
                            base_path=_BASE_PATH,
                            booking_id=booking_id,
                        ),
                        "/orders/{order_id}".format(order_id=order_id),
                        "/booked-offers/{booked_offer_id}".format(
                            booked_offer_id=booked_offer_id,
                        ),
                        "/booked-offer-parts/{booked_offer_part_id}".format(
                            booked_offer_part_id=booked_offer_part_id,
                        ),
                    ],
                ),
                headers=self._get_headers(),
            ),
        )
        return booking_response.GetBookedOfferPartResponse(**response.json())

    async def get_booked_trip(
        self,
        booking_id: str,
        order_id: str,
        booked_offer_id: str,
        booked_trip: str,
    ) -> booking_response.GetBookedTripResponse:
        response = await self._make_request(
            client.RequestOptions(
                method="GET",
                path="".join(
                    [
                        "{base_path}/{booking_id}".format(
                            base_path=_BASE_PATH,
                            booking_id=booking_id,
                        ),
                        "/orders/{order_id}".format(order_id=order_id),
                        "/booked-offers/{booked_offer_id}".format(
                            booked_offer_id=booked_offer_id,
                        ),
                        "/booked-trips/{booked_trip}".format(
                            booked_trip=booked_trip,
                        ),
                    ],
                ),
                headers=self._get_headers(),
            ),
        )
        return booking_response.GetBookedTripResponse(**response.json())

    async def get_fulfillment(
        self,
        booking_id: str,
        fulfillment_id: str,
    ) -> booking_response.GetFulfillmentResponse:
        response = await self._make_request(
            client.RequestOptions(
                method="GET",
                path="".join(
                    [
                        "{base_path}/{booking_id}".format(
                            base_path=_BASE_PATH,
                            booking_id=booking_id,
                        ),
                        "/fulfillments/{fulfillment_id}".format(
                            fulfillment_id=fulfillment_id,
                        ),
                    ],
                ),
                headers=self._get_headers(),
            ),
        )

        return booking_response.GetFulfillmentResponse(**response.json())

    async def get_refund_offer(
        self,
        booking_id: str,
        order_id: str,
        refund_offer_id: str,
    ) -> booking_response.GetRefundOfferResponse:
        response = await self._make_request(
            client.RequestOptions(
                method="GET",
                path="".join(
                    [
                        "{base_path}/{booking_id}".format(
                            base_path=_BASE_PATH,
                            booking_id=booking_id,
                        ),
                        "/orders/{order_id}".format(
                            order_id=order_id,
                        ),
                        "/refund-offers/{refund_offer_id}".format(
                            refund_offer_id=refund_offer_id,
                        ),
                    ],
                ),
                headers=self._get_headers(),
            ),
        )

        return booking_response.GetRefundOfferResponse(**response.json())


class OrdersClient(base.BenerailBaseClient):
    async def get_order(
        self,
        booking_id: str,
        order_id: str,
    ) -> booking_response.GetOrderResponse:
        response = await self._make_request(
            client.RequestOptions(
                method="GET",
                path="".join(
                    [
                        "{base_path}/{booking_id}".format(
                            base_path=_BASE_PATH,
                            booking_id=booking_id,
                        ),
                        "/orders/{order_id}".format(order_id=order_id),
                    ],
                ),
                headers=self._get_headers(),
            ),
        )

        return booking_response.GetOrderResponse(**response.json())

    async def delete_order(
        self,
        booking_id: str,
        order_id: str,
        etag: str,
    ) -> bool:
        response = await self._make_request(
            client.RequestOptions(
                method="DELETE",
                path="".join(
                    [
                        "{base_path}/{booking_id}".format(
                            base_path=_BASE_PATH,
                            booking_id=booking_id,
                        ),
                        "/orders/{order_id}".format(order_id=order_id),
                    ],
                ),
                headers=self._get_headers(etag),
            ),
        )

        return response.status_code == http.HTTPStatus.NO_CONTENT

    async def update_order_state(
        self,
        booking_id: str,
        order_id: str,
        etag: str,
        body: order.OrderIdBody,
    ) -> booking_response.GetOrderResponse:
        response = await self._make_request(
            client.RequestOptions(
                method="PATCH",
                path="".join(
                    [
                        "{base_path}/{booking_id}".format(
                            base_path=_BASE_PATH,
                            booking_id=booking_id,
                        ),
                        "/orders/{order_id}".format(order_id=order_id),
                    ],
                ),
                headers=self._get_headers(etag),
                payload=body.dict(by_alias=True, exclude_unset=True),
            ),
        )

        return booking_response.GetOrderResponse(**response.json())

    async def add_selected_offer_to_order(
        self,
        booking_id: str,
        order_id: str,
        etag: str,
        body: offer.SelectedOffersBody,
    ) -> booking_response.GetSelectedOfferResponse:
        response = await self._make_request(
            client.RequestOptions(
                method="POST",
                path="".join(
                    [
                        "{base_path}/{booking_id}".format(
                            base_path=_BASE_PATH,
                            booking_id=booking_id,
                        ),
                        "/orders/{order_id}".format(order_id=order_id),
                        "/selected-offers",
                    ],
                ),
                headers=self._get_headers(etag),
                payload=body.dict(by_alias=True, exclude_unset=True),
            ),
        )

        return booking_response.GetSelectedOfferResponse(**response.json())

    async def remove_selected_offer_from_order(
        self,
        booking_id: str,
        order_id: str,
        selected_offer_id: str,
        etag: str,
    ) -> bool:
        response = await self._make_request(
            client.RequestOptions(
                method="DELETE",
                path="".join(
                    [
                        "{base_path}/{booking_id}".format(
                            base_path=_BASE_PATH,
                            booking_id=booking_id,
                        ),
                        "/orders/{order_id}".format(order_id=order_id),
                        "/selected-offers/{selected_offer_id}".format(
                            selected_offer_id=selected_offer_id,
                        ),
                    ],
                ),
                headers=self._get_headers(etag),
            ),
        )

        return response.status_code == http.HTTPStatus.NO_CONTENT

    async def add_refund_to_order(
        self,
        booking_id: str,
        order_id: str,
        etag: str,
        body: order.OrderIdRefundOffersBody,
    ) -> booking_response.GetRefundOfferResponse:
        response = await self._make_request(
            client.RequestOptions(
                method="POST",
                path="".join(
                    [
                        "{base_path}/{booking_id}".format(
                            base_path=_BASE_PATH,
                            booking_id=booking_id,
                        ),
                        "/orders/{order_id}".format(order_id=order_id),
                        "/refund-offers",
                    ],
                ),
                headers=self._get_headers(etag),
                payload=body.dict(by_alias=True, exclude_unset=True),
            ),
        )

        return booking_response.GetRefundOfferResponse(**response.json())

    async def remove_refund_from_order(
        self,
        booking_id: str,
        order_id: str,
        refund_offer_id: str,
        etag: str,
    ) -> bool:
        response = await self._make_request(
            client.RequestOptions(
                method="DELETE",
                path="".join(
                    [
                        "{base_path}/{booking_id}".format(
                            base_path=_BASE_PATH,
                            booking_id=booking_id,
                        ),
                        "/orders/{order_id}".format(order_id=order_id),
                        "/refund-offers/{refund_offer_id}".format(
                            refund_offer_id=refund_offer_id,
                        ),
                    ],
                ),
                headers=self._get_headers(etag),
            ),
        )

        return response.status_code == http.HTTPStatus.NO_CONTENT


class SelectedOffersClient(base.BenerailBaseClient):
    async def get_selected_offer(
        self,
        booking_id: str,
        order_id: str,
        selected_offer_id: str,
    ) -> booking_response.GetSelectedOfferResponse:
        response = await self._make_request(
            client.RequestOptions(
                method="GET",
                path="".join(
                    [
                        "{base_path}/{booking_id}".format(
                            base_path=_BASE_PATH,
                            booking_id=booking_id,
                        ),
                        "/orders/{order_id}".format(order_id=order_id),
                        "/selected-offers/{selected_offer_id}".format(
                            selected_offer_id=selected_offer_id,
                        ),
                    ],
                ),
                headers=self._get_headers(),
            ),
        )
        return booking_response.GetSelectedOfferResponse(**response.json())

    async def get_selected_offer_part(
        self,
        booking_id: str,
        order_id: str,
        selected_offer_id: str,
        selected_offer_part_id: str,
    ) -> booking_response.GetSelectedOfferPartResponse:
        response = await self._make_request(
            client.RequestOptions(
                method="GET",
                path="".join(
                    [
                        "{base_path}/{booking_id}".format(
                            base_path=_BASE_PATH,
                            booking_id=booking_id,
                        ),
                        "/orders/{order_id}".format(order_id=order_id),
                        "/selected-offers/{selected_offer_id}".format(
                            selected_offer_id=selected_offer_id,
                        ),
                        "/selected-offer-parts/{selected_offer_part_id}".format(
                            selected_offer_part_id=selected_offer_part_id,
                        ),
                    ],
                ),
                headers=self._get_headers(),
            ),
        )
        return booking_response.GetSelectedOfferPartResponse(**response.json())

    async def update_selected_offer_part(  # noqa: WPS211
        self,
        booking_id: str,
        order_id: str,
        selected_offer_id: str,
        selected_offer_part_id: str,
        etag: str,
        body: offer.SelectedOfferPartIdBody,
    ) -> booking_response.GetSelectedOfferPartResponse:
        response = await self._make_request(
            client.RequestOptions(
                method="PATCH",
                path="".join(
                    [
                        "{base_path}/{booking_id}".format(
                            base_path=_BASE_PATH,
                            booking_id=booking_id,
                        ),
                        "/orders/{order_id}".format(order_id=order_id),
                        "/selected-offers/{selected_offer_id}".format(
                            selected_offer_id=selected_offer_id,
                        ),
                        "/selected-offer-parts/{selected_offer_part_id}".format(
                            selected_offer_part_id=selected_offer_part_id,
                        ),
                    ],
                ),
                headers=self._get_headers(etag),
                payload=body.dict(by_alias=True, exclude_unset=True),
            ),
        )
        return booking_response.GetSelectedOfferPartResponse(**response.json())


class PaymentsClient(base.BenerailBaseClient):
    async def create_payment_info_for_order(
        self,
        booking_id: str,
        order_id: str,
        etag: str,
        body: payment.OrderIdPaymentsBody,
    ) -> booking_response.GetPaymentResourceResponse:
        response = await self._make_request(
            client.RequestOptions(
                method="POST",
                path="".join(
                    [
                        "{base_path}/{booking_id}".format(
                            base_path=_BASE_PATH,
                            booking_id=booking_id,
                        ),
                        "/orders/{order_id}/payments".format(order_id=order_id),
                    ],
                ),
                headers=self._get_headers(etag),
                payload=body.dict(by_alias=True, exclude_unset=True),
            ),
        )

        return booking_response.GetPaymentResourceResponse(**response.json())

    async def get_payment_resource(
        self,
        booking_id: str,
        order_id: str,
        payment_id: str,
    ) -> booking_response.GetPaymentResourceResponse:
        response = await self._make_request(
            client.RequestOptions(
                method="GET",
                path="".join(
                    [
                        "{base_path}/{booking_id}".format(
                            base_path=_BASE_PATH,
                            booking_id=booking_id,
                        ),
                        "/orders/{order_id}".format(order_id=order_id),
                        "/payments/{payment_id}".format(payment_id=payment_id),
                    ],
                ),
                headers=self._get_headers(),
            ),
        )

        return booking_response.GetPaymentResourceResponse(**response.json())

    async def confirm_order_payment(  # noqa: WPS211
        self,
        booking_id: str,
        order_id: str,
        payment_id: str,
        etag: str,
        body: payment.PaymentIdBody,
    ) -> booking_response.GetPaymentResourceResponse:
        response = await self._make_request(
            client.RequestOptions(
                method="PATCH",
                path="".join(
                    [
                        "{base_path}/{booking_id}".format(
                            base_path=_BASE_PATH,
                            booking_id=booking_id,
                        ),
                        "/orders/{order_id}".format(order_id=order_id),
                        "/payments/{payment_id}".format(payment_id=payment_id),
                    ],
                ),
                headers=self._get_headers(etag),
                payload=body.dict(by_alias=True, exclude_unset=True),
            ),
        )

        return booking_response.GetPaymentResourceResponse(**response.json())
