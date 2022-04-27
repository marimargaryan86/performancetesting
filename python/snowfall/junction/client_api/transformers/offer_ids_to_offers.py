from typing import Sequence

from snowfall.adapter import offers as offers_adapter
from snowfall.junction.offers.v1alpha import models_pb2


class MissingOffersError(Exception):
    """Raised when not all offers where found."""


class OfferIdsToOffers(object):
    def __init__(
        self,
        offers_client: offers_adapter.Client,
    ):
        self._offers = offers_client

    async def transform(
        self,
        offer_ids: Sequence[str],
    ) -> list[models_pb2.OfferAggregate]:
        offers_page = await self._offers.find_by_ids(
            offer_ids,
            limit=len(offer_ids),
        )

        offer_ids_set = set(offer_ids)
        found_offer_ids_set = {offer.id for offer in offers_page.offers}

        if offer_ids_set != found_offer_ids_set:
            raise MissingOffersError(
                "Could not find offer ids: {0}".format(
                    offer_ids_set - found_offer_ids_set,
                ),
            )

        return list(offers_page.offers)
