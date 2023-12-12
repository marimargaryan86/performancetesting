from collections.abc import Mapping
from datetime import datetime

from starlette import requests

from snowfall.project.junction.go.service.orders.v1 import models_pb2, orders_pb2
from snowfall.stdlib.format import protobuf


def get_journey_filters(
    request: requests.Request,
    status_mapping: Mapping[str, models_pb2.Booking.Status.ValueType],
) -> list[orders_pb2.ListJourneysRequest.JourneyFilter]:
    filter_params = []

    date_filters = [
        ("order_created_at", "ge", request.query_params.get("filter[createdAt][ge]")),
        ("order_created_at", "le", request.query_params.get("filter[createdAt][le]")),
        ("departure_at", "ge", request.query_params.get("filter[departureDate][ge]")),
        ("departure_at", "le", request.query_params.get("filter[departureDate][le]")),
    ]
    status_query = request.query_params.get("filter[status][eq]")

    for filter_type, op, date_str in date_filters:
        if date_str:
            ts = protobuf.datetime_to_protobuf(datetime.fromisoformat(date_str))
            if filter_type == "order_created_at":
                filter_params.append(
                    orders_pb2.ListJourneysRequest.JourneyFilter(
                        operator=op,
                        order_created_at=ts,
                    ),
                )
            elif filter_type == "departure_at":
                filter_params.append(
                    orders_pb2.ListJourneysRequest.JourneyFilter(
                        operator=op,
                        departure_at=ts,
                    ),
                )

    if status_query is not None:
        booking_status = status_mapping.get(
            status_query,
            models_pb2.Booking.Status.STATUS_UNSPECIFIED,
        )
        filter_params.append(
            orders_pb2.ListJourneysRequest.JourneyFilter(
                operator="eq",
                booking_status=booking_status,
            ),
        )

    return filter_params
