import datetime

import lagom
import pydantic

from snowfall.adapter import authentication
from snowfall.project.junction.go.adapter import (  # noqa: WPS235
    legs,
    locations,
    offer_searches,
    offers,
    orders,
    places,
    price_quotes,
    schedules,
    segments,
    trip_candidate_searches,
    trip_candidates,
    trip_searches,
    trips,
)
from snowfall.project.junction.go.service.client_api import includes
from snowfall.stdlib.integration.starlette import application


class Settings(application.Settings):
    jwt_public_key: str
    jwt_token_version: str
    places_address: str
    offers_address: str
    orders_address: str
    trips_address: str
    schedules_address: str
    authentication_address: str
    ory_application_url: pydantic.AnyUrl
    ory_api_key: str
    ory_jwk_ttl: datetime.timedelta = datetime.timedelta(hours=1)
    validate_responses_against_spec: bool = True
    reseller_currencies: dict[str, str] = pydantic.Field(default_factory=dict)
    reseller_pay_companies: dict[str, str] = pydantic.Field(default_factory=dict)


def create_dependencies(  # noqa: WPS211
    authentication_client: authentication.Client,
    legs_client: legs.Client,
    locations_client: locations.Client,
    places_client: places.Client,
    price_quotes_client: price_quotes.Client,
    trip_searches_client: trip_searches.Client,
    trips_client: trips.Client,
    trip_candidate_searches_client: trip_candidate_searches.Client,
    trip_candidates_client: trip_candidates.Client,
    orders_client: orders.Client,
    offers_client: offers.Client,
    offer_searches_client: offer_searches.Client,
    segments_client: segments.Client,
    schedules_client: schedules.Client,
) -> lagom.Container:
    container = lagom.Container()
    container[authentication.Client] = authentication_client  # type: ignore[type-abstract]
    container[legs.Client] = legs_client  # type: ignore[type-abstract]
    container[locations.Client] = locations_client  # type: ignore[type-abstract]
    container[places.Client] = places_client  # type: ignore[type-abstract]
    container[price_quotes.Client] = price_quotes_client  # type: ignore[type-abstract]
    container[trip_searches.Client] = trip_searches_client  # type: ignore[type-abstract]
    container[trips.Client] = trips_client  # type: ignore[type-abstract]
    container[
        trip_candidate_searches.Client  # type: ignore[type-abstract]
    ] = trip_candidate_searches_client
    container[
        trip_candidates.Client  # type: ignore[type-abstract]
    ] = trip_candidates_client
    container[orders.Client] = orders_client  # type: ignore[type-abstract]
    container[offers.Client] = offers_client  # type: ignore[type-abstract]
    container[offer_searches.Client] = offer_searches_client  # type: ignore[type-abstract]
    container[segments.Client] = segments_client  # type: ignore[type-abstract]
    container[schedules.Client] = schedules_client  # type: ignore[type-abstract]

    includes.register_resolvers(
        legs_client=legs_client,
        offers_client=offers_client,
        segments_client=segments_client,
        orders_client=orders_client,
        schedules_client=schedules_client,
    )

    return container
