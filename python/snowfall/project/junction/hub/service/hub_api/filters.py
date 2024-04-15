from collections.abc import Mapping
from datetime import datetime

from starlette import requests

from snowfall.project.junction.go.service.orders.v1 import models_pb2, orders_pb2
from snowfall.project.junction.go.service.resellers.v1 import resellers_pb2
from snowfall.stdlib.format import protobuf


def get_journey_filters(
    request: requests.Request,
    status_mapping: Mapping[str, models_pb2.Booking.Status.ValueType],
) -> list[orders_pb2.ListJourneysRequest.JourneyFilter]:
    filter_params = _process_date_filters(request)
    filter_params += _process_status_filter(request, status_mapping)
    filter_params += _process_passenger_name_record_filter(request)
    filter_params += _process_last_name_filter(request)

    return filter_params


def get_reseller_filters(
    request: requests.Request,
) -> list[resellers_pb2.ListResellersRequest.ResellerFilter]:
    return _process_name_filter(request)


def _process_date_filters(
    request: requests.Request,
) -> list[orders_pb2.ListJourneysRequest.JourneyFilter]:
    date_filter_params = []
    date_filters = [
        ("order_created_at", "ge", request.query_params.get("filter[createdAt][ge]")),
        ("order_created_at", "le", request.query_params.get("filter[createdAt][le]")),
        ("departure_at", "ge", request.query_params.get("filter[departureDate][ge]")),
        ("departure_at", "le", request.query_params.get("filter[departureDate][le]")),
    ]

    for filter_type, op, date_str in date_filters:
        if date_str:
            ts = protobuf.datetime_to_protobuf(datetime.fromisoformat(date_str))
            if filter_type == "order_created_at":
                date_filter_params.append(
                    orders_pb2.ListJourneysRequest.JourneyFilter(
                        operator=op,
                        order_created_at=ts,
                    ),
                )
            elif filter_type == "departure_at":
                date_filter_params.append(
                    orders_pb2.ListJourneysRequest.JourneyFilter(
                        operator=op,
                        departure_at=ts,
                    ),
                )
    return date_filter_params


def _process_status_filter(
    request: requests.Request,
    status_mapping: Mapping[str, models_pb2.Booking.Status.ValueType],
) -> list[orders_pb2.ListJourneysRequest.JourneyFilter]:
    status_filter = request.query_params.get("filter[status][eq]")
    if status_filter is None:
        return []

    return [
        orders_pb2.ListJourneysRequest.JourneyFilter(
            operator="eq",
            booking_status=status_mapping.get(
                status_filter,
                models_pb2.Booking.Status.STATUS_UNSPECIFIED,
            ),
        ),
    ]


def _process_passenger_name_record_filter(
    request: requests.Request,
) -> list[orders_pb2.ListJourneysRequest.JourneyFilter]:
    passenger_name_record_filter = request.query_params.get("filter[pnr][eq]")
    if passenger_name_record_filter is None:
        return []

    return [
        orders_pb2.ListJourneysRequest.JourneyFilter(
            operator="eq",
            passenger_name_record=passenger_name_record_filter.strip().upper(),
        ),
    ]


def _process_last_name_filter(
    request: requests.Request,
) -> list[orders_pb2.ListJourneysRequest.JourneyFilter]:
    last_name_filter = request.query_params.get(
        "filter[passengerLastName][eq]",
    ) or request.query_params.get("filter[passengerLastName][like]")

    if last_name_filter is None:
        return []

    return [
        orders_pb2.ListJourneysRequest.JourneyFilter(
            operator="like",
            last_name=last_name_filter.strip(),
        ),
    ]


def _process_name_filter(
    request: requests.Request,
) -> list[resellers_pb2.ListResellersRequest.ResellerFilter]:
    name_filter = request.query_params.get("filter[name][like]")

    if name_filter is None:
        return []

    return [
        resellers_pb2.ListResellersRequest.ResellerFilter(
            operator="like",
            name=name_filter.strip(),
        ),
    ]
