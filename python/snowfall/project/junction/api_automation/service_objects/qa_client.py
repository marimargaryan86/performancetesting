import httpx

from snowfall.project.junction.api_automation.service_objects.air import (
    AirClient,
)
from snowfall.project.junction.api_automation.service_objects.car_rental import (
    CarRentalClient,
)
from snowfall.project.junction.api_automation.service_objects.client_wrapper import (
    ClientWrapper,
)
from snowfall.project.junction.api_automation.service_objects.places import (
    PlacesClient,
)


class QaClient(object):
    def __init__(
        self,
        base_url: str,
        auth: httpx.Auth | None = None,
        token: str | None = None,
        client: httpx.AsyncClient | None = None,
        sentry_url: str | None = None,
    ):
        self._client_wrapper = ClientWrapper(
            base_url,
            auth,
            token,
            client,
            sentry_url,
        )

        self.air = AirClient(self._client_wrapper)
        self.car_rental = CarRentalClient(self._client_wrapper)
        self.places = PlacesClient(self._client_wrapper)
