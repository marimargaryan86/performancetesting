from typing import AsyncIterator, Callable

from snowfall.project.junction.service.offers.v1alpha import models_pb2 as offers_pb2
from snowfall.project.junction.service.providers.ask2go import search, transformer
from snowfall.vendor.ask2go.models import search as search_model

OfferGroupGenerator = Callable[
    [search_model.CreateSearchCriteria],
    AsyncIterator[offers_pb2.OfferGroup],
]


def offer_group_generator(
    a2g_adapter: search.Adapter,
    a2g_transformer: transformer.OfferTransformer,
) -> OfferGroupGenerator:
    def wrapper(
        search_criteria: search_model.CreateSearchCriteria,
    ) -> AsyncIterator[offers_pb2.OfferGroup]:
        return a2g_transformer.to_offer_groups(
            a2g_adapter.gather_search_results(search_criteria),
        )

    return wrapper
