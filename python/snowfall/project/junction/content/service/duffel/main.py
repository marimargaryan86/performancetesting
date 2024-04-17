import uuid

import pydantic

from snowfall.project.junction.content import bootstrap
from snowfall.project.junction.content.service.duffel import offers, parsers, trips
from snowfall.project.junction.provider.v2alpha import meta_pb2
from snowfall.project.junction.v1 import segment_type_pb2
from snowfall.stdlib.service import application, grpc_factory, httpx_factory
from snowfall.vendor.duffel import client
from snowfall.vendor.rate_limiter import client as rate_limiter
from snowfall.vendor.rate_limiter import config, gubernator_pb2_grpc

_PROVIDER_ID = uuid.UUID("5d18e8e1-48e3-4b7c-82b9-62bd97a92f91")
_PROVIDER_NAME = "Duffel"


class _Settings(bootstrap.Settings):
    api_base_url: pydantic.AnyUrl
    api_key: str
    api_version: str = "v1"
    http_timeout: int = 30
    rate_limiter_grpc_host: str
    rate_limiter_service_configs: dict[str, config.RateLimitConfig]


async def _factory(
    app: application.Application[_Settings],
) -> bootstrap.ProviderConfiguration:
    httpx_client = await httpx_factory.make_client(app)
    rate_limit_client = rate_limiter.Client(
        gubernator_pb2_grpc.V1Stub(
            await grpc_factory.make_insecure_channel(
                app,
                app.settings.rate_limiter_grpc_host,
            ),
        ),
        app.settings.rate_limiter_service_configs["duffel"],
    )
    duffel_client = client.DuffelClient(
        http_client=httpx_client,
        api_base_url=str(app.settings.api_base_url),
        api_key=app.settings.api_key,
        version=app.settings.api_version,
        rate_limit_client=rate_limit_client,
    )
    trip_searcher = trips.Trips(
        search_client=duffel_client,
        transformer=trips.Transformer(trip_parser=parsers.TripParser()),
    )
    offer_searcher = offers.Offers(
        search_client=duffel_client,
        transformer=offers.Transformer(trip_parser=parsers.TripParser()),
    )

    return bootstrap.ProviderConfiguration(
        provider_id=_PROVIDER_ID,
        provider_name=_PROVIDER_NAME,
        trip_search_implementation=bootstrap.TripSearchImplementation(
            stop_identification_method=meta_pb2.TripSearchCapabilities.STOP_IDENTIFICATION_METHOD_IATA_CODES,
            supported_segment_types=[segment_type_pb2.SEGMENT_TYPE_FLIGHT],
            passenger_age_identification_method=meta_pb2.TripSearchCapabilities.PASSENGER_AGE_IDENTIFICATION_METHOD_DATE_OF_BIRTH,
            one_way=trip_searcher.find_one_way,
        ),
        offer_search_implementation=bootstrap.OfferSearchImplementation(
            one_way=offer_searcher.find_one_way,
        ),
    )


if __name__ == "__main__":
    entrypoint = bootstrap.Entrypoint(
        name="junction-content-duffel",
        implementation_factory=_factory,
        settings_class=_Settings,
    )
    entrypoint.enter()
