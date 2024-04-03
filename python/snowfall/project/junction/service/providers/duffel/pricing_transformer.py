from snowfall.project.junction.go.service.offers.v1 import models_pb2 as offers_pb2
from snowfall.project.junction.provider import parsers
from snowfall.project.junction.service.providers.duffel import cache
from snowfall.stdlib import money
from snowfall.stdlib.format import protobuf
from snowfall.stdlib.v1 import money_pb2
from snowfall.vendor.duffel.models.offer import Offer, OfferCondition


class PriceQuoteTransformer:
    def __init__(
        self,
        offer_cache: cache.OfferCache,
    ) -> None:
        self._offer_cache = offer_cache

    def to_price_quote(
        self,
        price_quote_id: str,
        offer: Offer,
        option_id: str,
    ) -> offers_pb2.PriceQuote:
        return offers_pb2.PriceQuote(
            id=price_quote_id,
            option_id=option_id,
            expires_at=protobuf.datetime_to_protobuf(offer.expires_at),
            price=self._to_money(offer.total_amount, offer.total_currency),
            price_breakdown=parsers.parse_price_breakdown(
                offer.base_amount,
                offer.tax_amount,
                offer.base_currency,
            ),
            required_documents=self._to_document_requirement(duffel_offer=offer),
            penalties=self._to_penalties(duffel_offer=offer),
        )

    def _to_money(self, amount: str, currency: str) -> money_pb2.Money:
        return money.from_string(amount, money.Currency(currency)).protobuf()

    def _to_document_requirement(
        self,
        duffel_offer: Offer,
    ) -> list[offers_pb2.PriceQuote.Required.ValueType]:
        required = list[offers_pb2.PriceQuote.Required.ValueType]()

        if duffel_offer.passenger_identity_documents_required:
            required.append(offers_pb2.PriceQuote.Required.REQUIRED_PASSPORT_NUMBER)
            required.append(offers_pb2.PriceQuote.Required.REQUIRED_NATIONALITY)
            required.append(offers_pb2.PriceQuote.Required.REQUIRED_ISSUING_COUNTRY)
            required.append(offers_pb2.PriceQuote.Required.REQUIRED_EXPIRATION_DATE)

        return required

    def _create_penalty(
        self,
        condition: OfferCondition | None,
        penalty_type: offers_pb2.Penalty.Type.ValueType,
    ) -> offers_pb2.Penalty:
        allowed = condition.allowed if condition else False
        price = None

        if condition and condition.penalty_amount and condition.penalty_currency:
            price = self._to_money(condition.penalty_amount, condition.penalty_currency)

        return offers_pb2.Penalty(
            penalty_type=penalty_type,
            applicability=offers_pb2.Penalty.Applicability.APPLICABILITY_BEFORE,
            changeable=penalty_type == offers_pb2.Penalty.Type.TYPE_EXCHANGE
            and allowed,
            refundable=penalty_type == offers_pb2.Penalty.Type.TYPE_REFUND and allowed,
            price=price,
        )

    def _to_penalties(
        self,
        duffel_offer: Offer,
    ) -> list[offers_pb2.Penalty]:
        penalties = list[offers_pb2.Penalty]()

        penalties.append(
            self._create_penalty(
                duffel_offer.conditions.change_before_departure,
                offers_pb2.Penalty.Type.TYPE_EXCHANGE,
            ),
        )
        penalties.append(
            self._create_penalty(
                duffel_offer.conditions.refund_before_departure,
                offers_pb2.Penalty.Type.TYPE_REFUND,
            ),
        )

        return penalties
