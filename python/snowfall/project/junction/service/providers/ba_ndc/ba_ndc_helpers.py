import datetime
import decimal
import itertools
from typing import Any

import more_itertools
import phonenumbers
import structlog
from google.protobuf import timestamp_pb2

from snowfall.project.junction.go.service.orders.v1alpha import amqp_pb2
from snowfall.stdlib import money, string
from snowfall.stdlib.format import protobuf
from snowfall.stdlib.v1alpha import datetime_pb2, models_pb2, money_pb2
from snowfall.vendor.ba_ndc.models import response_common_order_schemas

PROVIDER_NAME = "BA_NDC"


def get_last_travel_date(
    task: amqp_pb2.PlaceOrderTask,
) -> datetime.date:
    segments = itertools.chain(
        [tr.segment for tr in task.booking.trip_option.details],
    )

    return max(
        protobuf.protobuf_to_datetime(
            more_itertools.last(segment.legs).departure_at,
        ).date()
        for segment in segments
    )


def parse_phone_number(
    phone: str,
) -> phonenumbers.phonenumber.PhoneNumber:
    return phonenumbers.parse(phone)


def date_to_proto_now() -> timestamp_pb2.Timestamp:
    return protobuf.datetime_to_protobuf(
        datetime.datetime.now(tz=datetime.timezone.utc),
    )


def proto_to_date_time(date_time: datetime_pb2.DateTime) -> datetime.datetime:
    return protobuf.protobuf_to_datetime(date_time)


def proto_to_date(date: models_pb2.Date) -> datetime.date:
    return protobuf.protobuf_to_date(date)


def parse_price(price: response_common_order_schemas.PriceSimple) -> money_pb2.Money:
    return money.from_string(
        string_amount=price.total_amount,
        currency=money.Currency(price.currency),
    ).protobuf()


def str_to_decimal(amount: str) -> decimal.Decimal:
    return decimal.Decimal(amount)


def str_to_uuid(char_string: str) -> str:
    return string.to_uuid(char_string)


def get_logger(name: str) -> Any:
    return structlog.get_logger(name)
