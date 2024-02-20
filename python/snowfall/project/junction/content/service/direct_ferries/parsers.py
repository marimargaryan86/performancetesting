from snowfall.stdlib import money
from snowfall.stdlib.v1 import money_pb2


def amount_to_proto(
    amount: str | None,
    currency: str,
) -> money_pb2.Money:
    if not amount:
        return money.Money(0, money.Currency(currency)).protobuf()

    return money.from_string(amount, money.Currency(currency)).protobuf()
