import asyncio
import datetime
from typing import ClassVar

from snowfall.project.junction.go.service.offers.v1 import (
    grpc_pb2 as offers_grpc_pb2,
)
from snowfall.project.junction.go.service.offers.v1 import (
    grpc_pb2_grpc as offers_grpc_pb2_grpc,
)
from snowfall.project.junction.go.service.offers.v1 import (
    models_pb2 as offers_models_pb2,
)
from snowfall.project.junction.go.v1 import models_pb2 as go_models_pb2
from snowfall.service.deploy.verifiers import protocols
from snowfall.stdlib import string
from snowfall.stdlib.format import protobuf
from snowfall.stdlib.transport.grpc import client
from snowfall.stdlib.v1 import amqp_pb2 as stdlib_amqp_pb2
from snowfall.stdlib.v1 import latlng_pb2


class OfferSearchFlow(object):
    dependencies: ClassVar[protocols.Dependencies] = {("offers", "grpc")}
    environments: ClassVar[protocols.Environments] = {"development"}
    triggers: ClassVar[protocols.Triggers] = {"mock", "offers"}
    _cutoff = datetime.timedelta(seconds=30)  # noqa: WPS432

    async def run(
        self,
        environment: str,
        dependencies: protocols.ResolvedDependencies,
    ) -> None:
        offer_searches = offers_grpc_pb2_grpc.OfferSearchServiceStub(
            client.create_channel(
                "{0}:{1}".format(
                    dependencies[("offers", "grpc")][0],
                    dependencies[("offers", "grpc")][1],
                ),
            ),
        )
        offer_search = (
            await offer_searches.EnqueueOfferSearch(
                offers_grpc_pb2.EnqueueOfferSearchRequest(
                    search=_generate_offer_search(),
                ),
            )
        ).search

        cutoff = datetime.datetime.now(tz=datetime.UTC) + self._cutoff

        while _wait_for_offer_search(cutoff, offer_search):
            await asyncio.sleep(1)
            offer_search = (
                await offer_searches.GetOfferSearch(
                    offers_grpc_pb2.GetOfferSearchRequest(
                        id=offer_search.id,
                    ),
                )
            ).search

        if offer_search.status != stdlib_amqp_pb2.Trackable.STATUS_COMPLETED:
            raise RuntimeError


def _wait_for_offer_search(
    cutoff: datetime.datetime,
    offer_search: offers_models_pb2.OfferSearch,
) -> bool:
    return datetime.datetime.now(
        tz=datetime.UTC,
    ) < cutoff and offer_search.status in {
        stdlib_amqp_pb2.Trackable.STATUS_PENDING,
        stdlib_amqp_pb2.Trackable.STATUS_PROCESSING,
    }


def _generate_leg(identifier: str) -> go_models_pb2.Leg:
    return go_models_pb2.Leg(
        id=identifier,
        origin=_generate_point(string.uuid()),
        destination=_generate_point(string.uuid()),
        departure_at=protobuf.datetime_to_protobuf(
            datetime.datetime.now(tz=datetime.UTC),
        ),
        arrival_at=protobuf.datetime_to_protobuf(
            datetime.datetime.now(tz=datetime.UTC),
        ),
    )


def _generate_offer_search() -> offers_models_pb2.OfferSearch:
    return offers_models_pb2.OfferSearch(
        reseller_id="mock",
        currency_code="SEK",
        pay_company_id="e084bf91-500b-4a10-8c79-a0694797d490",
        session_token=string.uuid(),
        trip=offers_models_pb2.TripOfferSearch(
            trips=[
                go_models_pb2.Trip(
                    id=string.uuid(),
                    segments=[
                        go_models_pb2.Segment(
                            id=string.uuid(),
                            legs=[_generate_leg(string.uuid())],
                        ),
                    ],
                ),
            ],
            passengers=[
                offers_models_pb2.Passenger(
                    date_of_birth=protobuf.date_to_protobuf(
                        datetime.date(year=1987, month=5, day=24),  # noqa: WPS432
                    ),
                ),
            ],
            reseller_id="mock",
        ),
    )


def _generate_point(identifier: str) -> go_models_pb2.Point:
    return go_models_pb2.Point(
        ref=identifier,
        name="Point name",
        coordinates=latlng_pb2.LatLng(),
        time_zone="UTC",
    )
