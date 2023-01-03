import uuid
from typing import List, Sequence

from snowfall.project.junction.service.offers.v1alpha import models_pb2 as offers_pb2
from snowfall.project.junction.service.providers.ba_ndc import cache
from snowfall.stdlib import money
from snowfall.stdlib.format import protobuf
from snowfall.stdlib.v1alpha import money_pb2


def _to_money(amount: str, currency: str) -> money_pb2.Money | None:
    if amount and currency and currency != "":
        return money.from_string(amount, money.Currency(currency)).protobuf()

    return None


def _to_penalties(penalties: Sequence[cache.OfferPenalty]) -> List[offers_pb2.Penalty]:
    res = list[offers_pb2.Penalty]()

    if penalties:
        for penalty in penalties:
            if penalty is not None:
                res.append(
                    offers_pb2.Penalty(
                        penalty_type=offers_pb2.Penalty.Type.TYPE_REFUND
                        if penalty.penalty_type.lower().startswith("cancel")
                        else offers_pb2.Penalty.Type.TYPE_EXCHANGE,
                        applicability=offers_pb2.Penalty.Applicability.APPLICABILITY_BEFORE,
                        refundable=penalty.penalty_type.lower().startswith("cancel"),
                        changeable=penalty.penalty_type.lower().startswith("change"),
                        price=_to_money(penalty.price.amount, penalty.price.currency),
                    ),
                )

    return res


def _to_document_requirement(
    offer_details: cache.OfferDetails,
) -> List[offers_pb2.PriceQuote.Required.ValueType]:
    if offer_details.doc_required:
        return [
            offers_pb2.PriceQuote.Required.REQUIRED_PASSPORT_NUMBER,
            offers_pb2.PriceQuote.Required.REQUIRED_DATE_OF_BIRTH,
            offers_pb2.PriceQuote.Required.REQUIRED_NATIONALITY,
            offers_pb2.PriceQuote.Required.REQUIRED_ISSUING_COUNTRY,
            offers_pb2.PriceQuote.Required.REQUIRED_EXPIRATION_DATE,
        ]

    return []


class PriceQuoteTransformer(object):
    def __init__(
        self,
        offer_cache: cache.OfferCache,
    ) -> None:
        self._offer_cache = offer_cache

    def to_price_quote(
        self,
        offer_details: cache.OfferDetails,
        option_id: str,
    ) -> offers_pb2.PriceQuote:
        return offers_pb2.PriceQuote(
            id=str(uuid.uuid4()),
            option_id=option_id,
            expires_at=protobuf.datetime_to_protobuf(offer_details.expires_at),
            price=_to_money(offer_details.price.amount, offer_details.price.currency),
            penalties=_to_penalties(offer_details.penalties),
            required_documents=_to_document_requirement(offer_details),
        )
