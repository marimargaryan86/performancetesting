from __future__ import annotations

import uuid

import pydantic

from snowfall.project.junction.content import bootstrap
from snowfall.project.junction.content.service.direct_ferries import port, routes, trips
from snowfall.project.junction.provider.v2alpha import meta_pb2
from snowfall.project.junction.v1 import segment_type_pb2
from snowfall.stdlib import h3
from snowfall.stdlib.service import application, httpx_factory
from snowfall.vendor.direct_ferries import client
from snowfall.vendor.direct_ferries.clients import auth, base

_PROVIDER_ID = uuid.UUID("92ada881-f31c-471e-a8b0-01ed48a181d5")
_PROVIDER_NAME = "Direct Ferries"


class _Settings(bootstrap.Settings):
    api_base_url: pydantic.AnyUrl
    affiliate_api_url: str
    partner_code: str
    client_id: str
    client_secret: str
    api_version: str = "v1"
    http_timeout: int = 30


async def _factory(
    app: application.Application[_Settings],
) -> bootstrap.ProviderConfiguration:
    httpx_client = await httpx_factory.make_client(app)
    direct_ferries_client = client.DfHttpClient(
        http_client=httpx_client,
        auth_client=auth.AuthClient(
            api_url=str(app.settings.affiliate_api_url),
            client_secret=app.settings.client_secret,
            client_id=app.settings.client_id,
            http_client=httpx_client,
        ),
        config=base.ClientConfig(
            api_url=str(app.settings.api_base_url).rstrip("/"),
            partner_code=app.settings.partner_code,
            client_id=app.settings.client_id,
            client_secret=app.settings.client_secret,
            timeout=int(app.settings.http_timeout),
        ),
    )
    h3_port_mapping = h3.H3MappingRepository[port.Port](
        mapping=port.load_ports(),
        resolution=8,
    )
    trip_searcher = trips.Trips(
        search_client=direct_ferries_client,
        transformer=trips.Transformer(h3_port_mapping=h3_port_mapping),
        route_repo=routes.RouteRepository(),
        h3_port_mapping=h3.H3MappingRepository[port.Port](
            mapping=port.load_ports(),
            resolution=8,
        ),
    )

    return bootstrap.ProviderConfiguration(
        provider_id=_PROVIDER_ID,
        provider_name=_PROVIDER_NAME,
        trip_search_implementation=bootstrap.TripSearchImplementation(
            stop_identification_method=meta_pb2.TripSearchCapabilities.STOP_IDENTIFICATION_METHOD_COORDINATES,
            supported_segment_types=[segment_type_pb2.SEGMENT_TYPE_FERRY],
            passenger_age_identification_method=meta_pb2.TripSearchCapabilities.PASSENGER_AGE_IDENTIFICATION_METHOD_DATE_OF_BIRTH,
            one_way=trip_searcher.find_one_way,
            round_trip=trip_searcher.find_round_trip,
        ),
    )


if __name__ == "__main__":
    entrypoint = bootstrap.Entrypoint(
        name="junction-content-direct-ferries",
        implementation_factory=_factory,
        settings_class=_Settings,
    )
    entrypoint.enter()
