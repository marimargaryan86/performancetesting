from typing import AsyncIterator

from snowfall.project.junction.provider import offers
from snowfall.project.junction.service.offers.v1alpha import models_pb2 as offers_pb2
from snowfall.project.junction.service.providers.ask2go import search, transformer
from snowfall.project.junction.service.providers.ask2go.v1alpha import amqp_pb2
from snowfall.stdlib import string


def offer_group_cache_key(task: amqp_pb2.SearchCriteriaTask) -> str:
    return string.to_uuid(
        b"\x00".decode().join(
            [
                task.session_token,
                *[segment.id for segment in task.segments],
                task.criteria.cabin_class,
                str(task.criteria.adults),
                str(task.criteria.children),
                str(task.criteria.infants),
            ],
        ),
    )


def offer_group_generator(
    a2g_adapter: search.Adapter,
    a2g_transformer: transformer.OfferTransformer,
) -> offers.OfferGroupGenerator[amqp_pb2.SearchCriteriaTask]:
    def wrapper(
        search_task: amqp_pb2.SearchCriteriaTask,
    ) -> AsyncIterator[offers_pb2.OfferGroup]:
        return a2g_transformer.to_offer_groups(
            search_task,
            a2g_adapter.gather_search_results(search_task),
        )

    return wrapper
