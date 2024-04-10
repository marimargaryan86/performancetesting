import asyncio
import datetime
import random
from typing import NamedTuple

import httpx
import lagom
from grpc import aio
from motor import motor_asyncio

from snowfall.adapter import authentication as auth_adapter
from snowfall.project.junction.rocket.service.api.air import (
    repositories,
    types,
)
from snowfall.project.junction.rocket.service.api.air.transforms import (
    transforms as air_transforms,
)
from snowfall.project.junction.rocket.service.api.hotel import (
    repositories as hotel_repositories,
)
from snowfall.project.junction.rocket.service.api.hotel import (
    transformers as hotel_transforms,
)
from snowfall.project.junction.rocket.service.api.hotel import (
    types as hotel_types,
)
from snowfall.project.junction.rocket.service.api.settings import Settings
from snowfall.project.junction.rocket.service.places.v1alpha import places_pb2_grpc
from snowfall.project.junction.rocket.service.searches.v1alpha import grpc_pb2_grpc
from snowfall.service.authentication.v1 import oauth_pb2_grpc
from snowfall.stdlib.format import jwt
from snowfall.stdlib.integration.starlette import authentication as stdlib_auth
from snowfall.stdlib.service import application, grpc_factory
from snowfall.vendor.junction_one.auth import TemporaryTokenAuth
from snowfall.vendor.junction_one.client import JunctionOneClient


class _Channels(NamedTuple):
    authentication: aio.Channel
    searches: aio.Channel
    places: aio.Channel


async def create_dependencies(
    app: application.Application[Settings],
) -> lagom.Container:
    container = lagom.Container()

    channels = _Channels(
        *await asyncio.gather(
            grpc_factory.make_insecure_channel(
                app,
                app.settings.authentication_address,
            ),
            grpc_factory.make_insecure_channel(
                app,
                app.settings.searches_address,
            ),
            grpc_factory.make_insecure_channel(app, app.settings.places_address),
        ),
    )

    mongo = motor_asyncio.AsyncIOMotorClient(
        str(random.choice(app.settings.mongo_dsn)),  # noqa: S311
    )

    container[stdlib_auth.JWTAuthenticationBackend] = (
        stdlib_auth.JWTAuthenticationBackend(
            stdlib_auth.OryAuth(
                jwk_client=jwt.AsyncJWKClient(
                    jwk_url=auth_adapter.get_jwk_url(
                        app.settings.authentication_address,
                    ),
                    key_ttl=app.settings.ory_jwk_ttl,
                ),
                client_resolver=auth_adapter.oauth_client_resolver(
                    oauth_client=oauth_pb2_grpc.OAuthServiceStub(
                        channels.authentication,
                    ),
                ),
            ).get_owner_from_jwt,
        )
    )

    container[TemporaryTokenAuth] = TemporaryTokenAuth(
        api_key=app.settings.j_one_api_key,
        reseller_credentials_mapping=app.settings.reseller_j1_credentials_mapping,
    )

    container[datetime.timedelta] = app.settings.grpc_timeout
    container[grpc_pb2_grpc.SearchServiceStub] = grpc_pb2_grpc.SearchServiceStub(
        channels.searches,
    )
    container[grpc_pb2_grpc.SearchResultServiceStub] = (
        grpc_pb2_grpc.SearchResultServiceStub(channels.searches)
    )
    container[places_pb2_grpc.PlacesServiceStub] = places_pb2_grpc.PlacesServiceStub(
        channels.places,
    )
    container[JunctionOneClient] = JunctionOneClient(
        api_base_url=app.settings.j_one_api_base_url,
        http_client=await app.stack.enter_async_context(httpx.AsyncClient()),
        auth=container[TemporaryTokenAuth],
    )
    container[repositories.AirSearchRepository] = repositories.AirSearchRepository(
        collection=mongo.searches.air_results,
    )
    container[types.AirSearchRequestTransformer] = (  # type: ignore[type-abstract]
        air_transforms.AirSearchRequestTransformer
    )
    container[types.AirSearchResultTransformer] = (  # type: ignore[type-abstract]
        air_transforms.AirSearchResultTransformer
    )
    container[hotel_repositories.HotelSearchRepository] = (
        hotel_repositories.HotelSearchRepository(
            collection=mongo.searches.hotel_results,
        )
    )
    container[hotel_types.HotelSearchRequestTransformer] = (  # type: ignore[type-abstract]
        hotel_transforms.HotelSearchRequestTransformer
    )
    container[hotel_types.HotelSearchResultTransformer] = (  # type: ignore[type-abstract]
        hotel_transforms.HotelSearchResultTransformer
    )

    return container
