import itertools
from collections.abc import Sequence

from starlette import requests

from snowfall.project.junction.rocket.service.api.flights import models
from snowfall.project.junction.rocket.service.api.flights.repositories import (
    FlightSearchResultRepository,
)
from snowfall.stdlib.integration.starlette import includes


def _flights_offers_resolver(
    flights_results_repo: FlightSearchResultRepository,
) -> includes.ResolverFunc:
    async def wrapper(
        identifiers: Sequence[str],
        request: requests.Request,
    ) -> Sequence[models.OfferResource]:
        response_results = await flights_results_repo.find_results_by_offer_ids(
            identifiers=identifiers,
        )
        offers = list(
            itertools.chain.from_iterable([
                result.offers async for result in response_results
            ]),
        )

        return [models.OfferResource.from_model(offer) for offer in offers]

    return wrapper


def _flights_result_details_resolver(
    flights_results_repo: FlightSearchResultRepository,
) -> includes.ResolverFunc:
    async def wrapper(
        identifiers: Sequence[str],
        request: requests.Request,
    ) -> Sequence[models.ResultDetailResource]:
        response_results = await flights_results_repo.find_results_by_result_detail_ids(
            identifiers=identifiers,
        )
        result_details = list(
            itertools.chain.from_iterable([
                result.result_details async for result in response_results
            ]),
        )

        return [
            models.ResultDetailResource.from_model(result_detail)
            for result_detail in result_details
        ]

    return wrapper


def register_resolvers(
    flights_results_repo: FlightSearchResultRepository,
) -> None:
    resolvers = (
        includes.Resolver(
            resource=models.OfferResource,
            func=_flights_offers_resolver(flights_results_repo),
        ),
        includes.Resolver(
            resource=models.ResultDetailResource,
            func=_flights_result_details_resolver(flights_results_repo),
        ),
    )

    for resolver in resolvers:
        includes.add_resolver(resolver)
