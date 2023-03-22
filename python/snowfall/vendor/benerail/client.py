import httpx

from snowfall.vendor.benerail.clients import bookings as booking_client
from snowfall.vendor.benerail.clients import dialogue as dialog_client
from snowfall.vendor.benerail.clients import (
    price_calendar,
    products,
    rcode,
    trip_offers,
    trips,
)


class BenerailClient(object):  # noqa: WPS214
    def __init__(
        self,
        subscription_key: str,
        base_url: str,
        http_client: httpx.AsyncClient,
    ):
        self._dialogues_client = dialog_client.DialoguesClient(
            subscription_key,
            base_url,
            http_client,
        )

        self._trip_filters_client = dialog_client.TripFiltersClient(
            subscription_key,
            base_url,
            http_client,
        )

        self._trip_offer_filters_client = dialog_client.TripOfferFiltersClient(
            subscription_key,
            base_url,
            http_client,
        )

        self._passengers_client = dialog_client.PassengersClient(
            subscription_key,
            base_url,
            http_client,
        )

        self._bookers_client = dialog_client.BookersClient(
            subscription_key,
            base_url,
            http_client,
        )

        self._bookings_client = booking_client.BookingsClient(
            subscription_key,
            base_url,
            http_client,
        )

        self._orders_client = booking_client.OrdersClient(
            subscription_key,
            base_url,
            http_client,
        )

        self._selected_offers_client = booking_client.SelectedOffersClient(
            subscription_key,
            base_url,
            http_client,
        )

        self._payments_client = booking_client.PaymentsClient(
            subscription_key,
            base_url,
            http_client,
        )

        self._rcode_client = rcode.RcodeClient(
            subscription_key,
            base_url,
            http_client,
        )

        self._rcode_type_client = rcode.RcodeTypeClient(
            subscription_key,
            base_url,
            http_client,
        )

        self._place_client = rcode.PlaceClient(
            subscription_key,
            base_url,
            http_client,
        )

        self._price_calendar_client = price_calendar.PriceCalendarClient(
            subscription_key,
            base_url,
            http_client,
        )

        self._products_client = products.ProductsClient(
            subscription_key,
            base_url,
            http_client,
        )

        self._trips_client = trips.TripsClient(
            subscription_key,
            base_url,
            http_client,
        )

        self._trip_offers_client = trip_offers.TripOffersClient(
            subscription_key,
            base_url,
            http_client,
        )

        self._offers_client = trip_offers.OffersClient(
            subscription_key,
            base_url,
            http_client,
        )

    @property
    def dialogue(self) -> dialog_client.DialoguesClient:
        return self._dialogues_client

    @property
    def trip_filter(self) -> dialog_client.TripFiltersClient:
        return self._trip_filters_client

    @property
    def trip_offer_filter_client(self) -> dialog_client.TripOfferFiltersClient:
        return self._trip_offer_filters_client

    @property
    def passengers_client(self) -> dialog_client.PassengersClient:
        return self._passengers_client

    @property
    def bookers_client(self) -> dialog_client.BookersClient:
        return self._bookers_client

    @property
    def bookings_client(self) -> booking_client.BookingsClient:
        return self._bookings_client

    @property
    def orders_client(self) -> booking_client.OrdersClient:
        return self._orders_client

    @property
    def selected_offers_client(self) -> booking_client.SelectedOffersClient:
        return self._selected_offers_client

    @property
    def payments_client(self) -> booking_client.PaymentsClient:
        return self._payments_client

    @property
    def rcode_client(self) -> rcode.RcodeClient:
        return self._rcode_client

    @property
    def rcode_type_client(self) -> rcode.RcodeTypeClient:
        return self._rcode_type_client

    @property
    def place(self) -> rcode.PlaceClient:
        return self._place_client

    @property
    def price_calendar_client(self) -> price_calendar.PriceCalendarClient:
        return self._price_calendar_client

    @property
    def products_client(self) -> products.ProductsClient:
        return self._products_client

    @property
    def trips_client(self) -> trips.TripsClient:
        return self._trips_client

    @property
    def trip_offers_client(self) -> trip_offers.TripOffersClient:
        return self._trip_offers_client

    @property
    def offers_client(self) -> trip_offers.OffersClient:
        return self._offers_client
