import asyncio
import datetime
from typing import ClassVar

from grpc import aio

from snowfall.project.junction.go.service.offers.v1 import (
    grpc_pb2 as offers_grpc_pb2,
)
from snowfall.project.junction.go.service.offers.v1 import (
    grpc_pb2_grpc as offers_grpc_pb2_grpc,
)
from snowfall.project.junction.go.service.offers.v1 import (
    models_pb2 as offers_models_pb2,
)
from snowfall.project.junction.go.v1 import models_pb2 as go_models_pb2
from snowfall.service.deploy.verifiers import protocols
from snowfall.stdlib import string
from snowfall.stdlib.format import protobuf
from snowfall.stdlib.logging import stdout
from snowfall.stdlib.v1 import amqp_pb2 as stdlib_amqp_pb2
from snowfall.stdlib.v1 import latlng_pb2


class OrdersFlow(object):
    dependencies: ClassVar[protocols.Dependencies] = {("offers", "grpc")}
    environments: ClassVar[protocols.Environments] = {"development"}
    _cutoff = datetime.timedelta(seconds=30)  # noqa: WPS432
    _logger = stdout.get_logger()

    async def run(
        self,
        environment: str,
        dependencies: protocols.ResolvedDependencies,
    ) -> None:
        self._initialize(dependencies)

        self._logger.info("Verifying OfferSearch step...")
        offer_search = await self._prepare_offer_search()
        if offer_search.status != stdlib_amqp_pb2.Trackable.STATUS_COMPLETED:
            self._logger.error("OfferSearch step: FAILED")
            raise RuntimeError(
                "OfferSearch Flow failed! Bad OfferSearch status: {0}".format(
                    offer_search,
                ),
            )
        self._logger.info("OfferSearch step: SUCCEEDED")

        self._logger.info("Retrieving Offer and option...")
        offer, option = await self._get_offer_and_option(offer_search)

        self._logger.info("Verifying PriceQuote step...")
        price_quote = await self._prepare_price_quote(offer, option)
        if not price_quote.quotes:
            self._logger.error("PriceQuote step: FAILED")
            raise RuntimeError(
                "PriceQuote Flow failed! Empty quotes: {0}".format(
                    price_quote,
                ),
            )
        self._logger.info("PriceQuote step: SUCCEEDED")

    def _initialize(self, dependencies: protocols.ResolvedDependencies) -> None:
        channel = aio.insecure_channel(
            "{0}:{1}".format(
                dependencies[("offers", "grpc")][0],
                dependencies[("offers", "grpc")][1],
            ),
        )
        self._price_quotes_stub = offers_grpc_pb2_grpc.PriceQuoteServiceStub(channel)
        self._offer_searches_stub = offers_grpc_pb2_grpc.OfferSearchServiceStub(channel)
        self._offers_stub = offers_grpc_pb2_grpc.OfferServiceStub(channel)
        self._generated_offer_search = _generate_offer_search()

    async def _prepare_price_quote(
        self,
        offer: offers_models_pb2.OfferAggregate,
        option: offers_models_pb2.Offer,
    ) -> offers_models_pb2.PriceQuoteContainer:
        price_quote = (
            await self._price_quotes_stub.CreatePriceQuote(
                offers_grpc_pb2.CreatePriceQuoteRequest(
                    offer_id=offer.id,
                    option_ids=[option.id],
                    session_token=self._generated_offer_search.session_token,
                    pay_company_id=self._generated_offer_search.pay_company_id,
                    reseller_id=self._generated_offer_search.reseller_id,
                ),
            )
        ).price_quote

        cutoff = datetime.datetime.now(tz=datetime.UTC) + self._cutoff
        while _wait_for_price_quote(cutoff, price_quote):
            await asyncio.sleep(1)
            price_quote = (
                await self._price_quotes_stub.GetPriceQuote(
                    offers_grpc_pb2.GetPriceQuoteRequest(
                        id=price_quote.id,
                    ),
                )
            ).price_quote
        return price_quote

    async def _get_offer_and_option(
        self,
        offer_search: offers_models_pb2.OfferSearch,
    ) -> tuple[offers_models_pb2.OfferAggregate, offers_models_pb2.Offer]:
        aggregates = (
            await self._offers_stub.ListOffers(
                offers_grpc_pb2.ListOffersRequest(
                    page_token="",
                    offer_search_ids=offers_grpc_pb2.ListOfIds(
                        ids=[offer_search.id],
                    ),
                ),
                timeout=10,
            )
        ).offers

        if not aggregates:
            self._logger.error("No OfferAggregate was found for OfferSearch")
            raise RuntimeError(
                "No OfferAggregate was found for: {0}".format(offer_search),
            )
        aggregate = aggregates[0]

        if not aggregate.groups:
            self._logger.error("No OfferGroup was found for Offer")
            raise RuntimeError("No Offer Group was found for: {0}".format(aggregate))
        group = aggregate.groups[0]

        if not group.offers:
            self._logger.error("No Offer was found for OfferGroup")
            raise RuntimeError(
                "No Offer was found for OfferGroup: {0}".format(aggregate),
            )
        return aggregate, group.offers[0]

    async def _prepare_offer_search(self) -> offers_models_pb2.OfferSearch:
        offer_search = (
            await self._offer_searches_stub.EnqueueOfferSearch(
                offers_grpc_pb2.EnqueueOfferSearchRequest(
                    search=self._generated_offer_search,
                ),
            )
        ).search
        cutoff = datetime.datetime.now(tz=datetime.UTC) + self._cutoff

        while _wait_for_offer_search(cutoff, offer_search):
            await asyncio.sleep(1)
            offer_search = (
                await self._offer_searches_stub.GetOfferSearch(
                    offers_grpc_pb2.GetOfferSearchRequest(
                        id=offer_search.id,
                    ),
                )
            ).search
        return offer_search


def _wait_for_offer_search(
    cutoff: datetime.datetime,
    offer_search: offers_models_pb2.OfferSearch,
) -> bool:
    return datetime.datetime.now(
        tz=datetime.UTC,
    ) < cutoff and offer_search.status in {
        stdlib_amqp_pb2.Trackable.STATUS_PENDING,
        stdlib_amqp_pb2.Trackable.STATUS_PROCESSING,
    }


def _wait_for_price_quote(
    cutoff: datetime.datetime,
    price_quote: offers_models_pb2.PriceQuoteContainer,
) -> bool:
    return (
        datetime.datetime.now(
            tz=datetime.UTC,
        )
        < cutoff
        and not price_quote.quotes
    )


def _generate_leg(identifier: str) -> go_models_pb2.Leg:
    return go_models_pb2.Leg(
        id=identifier,
        origin=_generate_point(string.uuid()),
        destination=_generate_point(string.uuid()),
        departure_at=protobuf.datetime_to_protobuf(
            datetime.datetime.now(tz=datetime.UTC),
        ),
        arrival_at=protobuf.datetime_to_protobuf(
            datetime.datetime.now(tz=datetime.UTC),
        ),
    )


def _generate_offer_search() -> offers_models_pb2.OfferSearch:
    return offers_models_pb2.OfferSearch(
        reseller_id="mock",
        currency_code="SEK",
        pay_company_id="e084bf91-500b-4a10-8c79-a0694797d490",
        session_token=string.uuid(),
        trip=offers_models_pb2.TripOfferSearch(
            trips=[
                go_models_pb2.Trip(
                    id=string.uuid(),
                    segments=[
                        go_models_pb2.Segment(
                            id=string.uuid(),
                            legs=[_generate_leg(string.uuid())],
                        ),
                    ],
                ),
            ],
            passengers=[
                offers_models_pb2.Passenger(
                    date_of_birth=protobuf.date_to_protobuf(
                        datetime.date(year=1987, month=5, day=24),  # noqa: WPS432
                    ),
                ),
            ],
            reseller_id="mock",
        ),
    )


def _generate_point(identifier: str) -> go_models_pb2.Point:
    return go_models_pb2.Point(
        ref=identifier,
        name="Point name",
        coordinates=latlng_pb2.LatLng(),
        time_zone="UTC",
    )
