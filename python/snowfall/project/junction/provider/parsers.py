from snowfall.project.junction.go.service.offers.v1 import (
    models_pb2 as offer_models_pb2,
)
from snowfall.stdlib import money


def parse_price_breakdown(
    base_fare: str,
    tax_amount: str | None,
    currency: str,
) -> list[offer_models_pb2.PriceBreakdown]:
    price_breakdown = list[offer_models_pb2.PriceBreakdown]()

    price_breakdown.append(
        offer_models_pb2.PriceBreakdown(
            price=money.from_string(
                base_fare,
                money.Currency(currency),
            ).protobuf(),
            breakdown_type=offer_models_pb2.PriceBreakdown.BreakdownType.BREAKDOWN_TYPE_BASE_FARE,
        ),
    )

    if tax_amount:
        price_breakdown.append(
            offer_models_pb2.PriceBreakdown(
                price=money.from_string(
                    tax_amount,
                    money.Currency(currency),
                ).protobuf(),
                breakdown_type=offer_models_pb2.PriceBreakdown.BreakdownType.BREAKDOWN_TYPE_TAX,
            ),
        )

    return price_breakdown
