from snowfall.adapter import offers as offers_adapter
from snowfall.junction.offers.v1alpha import offers_pb2


class MissingOffersError(Exception):
    """Raised when not all trips where found."""


class OfferIdsToOffers(object):
    def __init__(
        self,
        offers_client: offers_adapter.Client,
    ):
        self._offers = offers_client

    async def transform(self, offer_ids: list[str]) -> list[offers_pb2.Offer]:
        offers = []
        for offer_id in offer_ids:
            try:
                offers.append(await self._offers.get(offer_id))
            except offers_adapter.NotFoundError:
                raise MissingOffersError(
                    "Offer with id: '{0}' not found.".format(offer_id),
                )

        return offers
