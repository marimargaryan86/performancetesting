from collections.abc import Sequence

from snowfall.project.junction.go.service.offers.v1 import models_pb2 as offers_pb2
from snowfall.project.junction.provider import parsers
from snowfall.project.junction.service.providers.ba_ndc import cache
from snowfall.stdlib import money
from snowfall.stdlib.format import protobuf
from snowfall.stdlib.v1 import money_pb2


def _to_money(amount: str, currency: str) -> money_pb2.Money | None:
    if amount and currency and currency != "":
        return money.from_string(amount, money.Currency(currency)).protobuf()

    return None


def _to_penalties(penalties: Sequence[cache.OfferPenalty]) -> list[offers_pb2.Penalty]:
    return [
        offers_pb2.Penalty(
            penalty_type=(
                offers_pb2.Penalty.Type.TYPE_REFUND
                if penalty.penalty_type.lower().startswith("cancel")
                else offers_pb2.Penalty.Type.TYPE_EXCHANGE
            ),
            applicability=offers_pb2.Penalty.Applicability.APPLICABILITY_BEFORE,
            refundable=penalty.penalty_type.lower().startswith("cancel"),
            changeable=penalty.penalty_type.lower().startswith("change"),
            price=_to_money(penalty.price.amount, penalty.price.currency),
        )
        for penalty in penalties
    ]


def _to_document_requirement(
    price_quote_details: cache.PriceQuoteDetails,
) -> list[offers_pb2.PriceQuote.Required.ValueType]:
    required_docs: list[offers_pb2.PriceQuote.Required.ValueType] = []

    if price_quote_details.is_international_flight:
        required_docs.extend(
            [
                offers_pb2.PriceQuote.Required.REQUIRED_NATIONALITY,
                offers_pb2.PriceQuote.Required.REQUIRED_EXPIRATION_DATE,
                offers_pb2.PriceQuote.Required.REQUIRED_ISSUING_COUNTRY,
                offers_pb2.PriceQuote.Required.REQUIRED_PASSPORT_NUMBER,
                offers_pb2.PriceQuote.Required.REQUIRED_RESIDENCE_COUNTRY_CODE,
            ],
        )

    if price_quote_details.has_flight_with_usa_destination:
        required_docs.append(
            offers_pb2.PriceQuote.Required.REQUIRED_RESIDENCE_ADDRESS,
        )

    return required_docs


class PriceQuoteTransformer(object):
    def to_price_quote(
        self,
        price_quote_details_id: str,
        price_quote_details: cache.PriceQuoteDetails,
        option_id: str,
    ) -> offers_pb2.PriceQuote:
        return offers_pb2.PriceQuote(
            id=price_quote_details_id,
            option_id=option_id,
            expires_at=protobuf.datetime_to_protobuf(price_quote_details.expires_at),
            price=_to_money(
                price_quote_details.price.amount,
                price_quote_details.price.currency,
            ),
            price_breakdown=parsers.parse_price_breakdown(
                price_quote_details.price_breakdown.base_amount,
                price_quote_details.price_breakdown.tax_amount,
                price_quote_details.price_breakdown.currency,
            ),
            penalties=_to_penalties(price_quote_details.penalties),
            required_documents=_to_document_requirement(price_quote_details),
        )
