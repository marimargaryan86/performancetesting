import httpx

from snowfall.vendor.benerail.clients import dialogue as dialog_client


class BenerailClient(object):
    def __init__(
        self,
        subscription_key: str,
        base_url: str,
        http_client: httpx.AsyncClient,
    ):
        self._dialogue = dialog_client.DialogueClient(
            subscription_key,
            base_url,
            http_client,
        )
        self._trip_filter = dialog_client.TripFilterClient(
            subscription_key,
            base_url,
            http_client,
        )
        self._trip_offer_filter_client = dialog_client.TripOfferFilterClient(
            subscription_key,
            base_url,
            http_client,
        )

    @property
    def dialogue(self) -> dialog_client.DialogueClient:
        return self._dialogue

    @property
    def trip_filter(self) -> dialog_client.TripFilterClient:
        return self._trip_filter

    @property
    def trip_offer_filter_client(self) -> dialog_client.TripOfferFilterClient:
        return self._trip_offer_filter_client
