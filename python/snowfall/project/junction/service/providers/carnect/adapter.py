from collections.abc import AsyncIterator

from snowfall.project.junction.go.service.offers.v1 import (
    models_pb2 as offer_models_pb2,
)
from snowfall.project.junction.service.providers.carnect.v1 import amqp_pb2


class CarnectOffersAdapter(object):
    async def gather_offer_groups(
        self,
        search_task: amqp_pb2.Criteria,
    ) -> AsyncIterator[offer_models_pb2.OfferGroup]:
        yield offer_models_pb2.OfferGroup()
