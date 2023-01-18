from snowfall.vendor.ba_ndc.models import (
    response_common_offer_schemas,
    response_order_schemas,
)


class OrderViewAdapter(object):
    order_response: response_order_schemas.OrderResponse

    def __init__(
        self,
        order_response: response_order_schemas.OrderResponse,
    ) -> None:
        self.order_response = order_response

    def get_pnr(self) -> str:
        if self.is_success():
            return self.order_response.order.pnr

        return ""

    def get_booking_result(self) -> response_order_schemas.OrderResponse:
        return self.order_response

    def get_order(self) -> response_order_schemas.Order:
        return self.order_response.order

    def is_success(self) -> bool:
        return self.order_response.order is not None

    def get_passengers(self) -> list[response_order_schemas.Passenger]:
        return self.order_response.passengers or []

    def get_segments(self) -> list[response_common_offer_schemas.Segment]:
        return self.order_response.segments or []
