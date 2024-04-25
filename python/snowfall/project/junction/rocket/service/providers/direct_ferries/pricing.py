import datetime

from snowfall.project.junction.rocket.service.providers.direct_ferries import cache
from snowfall.project.junction.rocket.service.searches.v1alpha import (
    amqp_pb2,
    models_pb2,
)
from snowfall.stdlib import money
from snowfall.stdlib.format import protobuf
from snowfall.stdlib.transport.amqp import consumer, producer, types
from snowfall.vendor.direct_ferries import client
from snowfall.vendor.direct_ferries.models import passenger


class SearchError(Exception):
    """Raised when there is an exception in the Direct Ferries quote search."""


class QuoteResultProducer:
    def __init__(self, producer_obj: producer.Producer, routing_key: str):
        self._producer = producer_obj
        self._routing_key = routing_key

    async def publish(self, message: amqp_pb2.QuoteTaskResult) -> None:
        await self._producer.publish(message, self._routing_key)


class QuoteTaskConsumer:
    def __init__(
        self,
        df_client: client.DfHttpClient,
        consumer_obj: consumer.Consumer[amqp_pb2.QuoteTask],
        quote_result_producer: QuoteResultProducer,
        offers_cache: cache.OffersCache,
        quote_cache: cache.QuoteCache,
        ttl: datetime.timedelta,
        pay_company_id: str,
    ):
        self._df_client = df_client
        self._consumer = consumer_obj
        self._quote_result_producer = quote_result_producer
        self._offers_cache = offers_cache
        self._quote_cache = quote_cache
        self._ttl = ttl
        self._pay_company_id = pay_company_id

    async def consume(self) -> None:
        await self._consumer.consume(self._process_message)

    async def _process_message(
        self,
        message: types.Message[amqp_pb2.QuoteTask],
    ) -> None:
        offer_id = message.body.quote.offer_ids[0]
        offer_cache = await self._offers_cache.fetch(offer_id)

        if not offer_cache:
            raise SearchError("Offer not found")

        passenger_requirements = await self._get_combined_passenger_requirements(
            offer_cache,
        )

        required_passenger_information = self._generate_passenger_requirement_response(
            passenger_requirements,
        )

        expires_at = datetime.datetime.now(tz=datetime.UTC) + self._ttl

        await self._quote_cache.store(
            cache.OfferDetails(quote=offer_cache.quote),
            expires_at=expires_at,
        )

        base_price_proto = money.from_string(
            str(offer_cache.quote.price.total_in_selected_currency),
            money.Currency(offer_cache.quote.selected_currency),
        ).protobuf()

        quote_obj = models_pb2.Quote(
            pay_company_id=self._pay_company_id,
            expires_at=protobuf.datetime_to_protobuf(expires_at),
            total_price=base_price_proto,
            quoted_offers=[
                models_pb2.QuotedOffer(
                    offer_id=offer_id,
                    price=base_price_proto,
                    required_documents=required_passenger_information,
                    rules=[
                        models_pb2.FareRule(
                            title="Ticket conditions",
                            body=offer_cache.quote.ticket_conditions or "",
                        ),
                    ],
                    price_breakdown=[
                        models_pb2.PriceBreakdown(
                            price=base_price_proto,
                            breakdown_type=models_pb2.PriceBreakdown.BREAKDOWN_TYPE_BASE_FARE,
                        ),
                    ],
                ),
            ],
        )

        quote_obj.MergeFrom(message.body.quote)

        await self._quote_result_producer.publish(
            message=amqp_pb2.QuoteTaskResult(
                quote=quote_obj,
                reseller_id=message.body.reseller_id,
            ),
        )

    async def _get_combined_passenger_requirements(
        self,
        offer_cache: cache.OfferDetails,
    ) -> passenger.RoutePassengerInfo:
        outbound_leg = offer_cache.quote.legs[0]
        inbound_leg = offer_cache.quote.legs[-1]

        outbound = (
            await self._df_client.routes.get_passenger_info_by_route_and_operator(
                operator_id=outbound_leg.operator.identifier,
                route_id=outbound_leg.route_id,
            )
        )

        if inbound_leg.is_return_leg is False:
            return outbound

        inbound = await self._df_client.routes.get_passenger_info_by_route_and_operator(
            operator_id=inbound_leg.operator.identifier,
            route_id=inbound_leg.route_id,
        )

        return passenger.RoutePassengerInfo(
            need_nationality=outbound.need_nationality or inbound.need_nationality,
            need_place_of_birth=outbound.need_place_of_birth
            or inbound.need_place_of_birth,
            need_date_of_birth=outbound.need_date_of_birth
            or inbound.need_date_of_birth,
            need_passport=outbound.need_passport or inbound.need_passport,
            need_passport_start_date=outbound.need_passport_start_date
            or inbound.need_passport_start_date,
            need_passport_expiry_date=outbound.need_passport_expiry_date
            or inbound.need_passport_expiry_date,
        )

    def _generate_passenger_requirement_response(
        self,
        passenger_requirements: passenger.RoutePassengerInfo,
    ) -> list[models_pb2.QuotedOffer.Required.ValueType]:
        requirements = []

        if passenger_requirements.need_date_of_birth:
            requirements.append(models_pb2.QuotedOffer.Required.REQUIRED_DATE_OF_BIRTH)

        if passenger_requirements.need_nationality:
            requirements.append(models_pb2.QuotedOffer.Required.REQUIRED_NATIONALITY)

        if passenger_requirements.need_passport_expiry_date:
            requirements.append(
                models_pb2.QuotedOffer.Required.REQUIRED_EXPIRATION_DATE,
            )

        if passenger_requirements.need_passport:
            requirements.append(
                models_pb2.QuotedOffer.Required.REQUIRED_PASSPORT_NUMBER,
            )

        if passenger_requirements.need_passport_start_date:
            requirements.append(models_pb2.QuotedOffer.Required.REQUIRED_ISSUE_DATE)

        return requirements
