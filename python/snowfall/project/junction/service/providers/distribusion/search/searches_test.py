import datetime
import zoneinfo

from snowfall.project.junction.go.service.offers.v1alpha import (
    models_pb2 as offer_models_pb2,
)
from snowfall.project.junction.service.providers.distribusion.conftest import (
    disable_by_default,
)
from snowfall.project.junction.service.providers.distribusion.search.adapter import (
    DistribusionSearchAdapter,
)
from snowfall.project.junction.service.providers.distribusion.v1alpha import amqp_pb2
from snowfall.stdlib.format import protobuf
from snowfall.stdlib.v1alpha import models_pb2

_DEFAULT_PASSENGER_AGE = 40
_DEPARTURE_IN_DAYS = 11
_DEBERCBS_FRPARPGB_CRITERIA = amqp_pb2.Criteria(
    origin_ids=["DEBERCBS"],
    destination_ids=["FRPARPGB"],
    outbound_departure=protobuf.date_to_protobuf(
        datetime.date.today() + datetime.timedelta(days=_DEPARTURE_IN_DAYS),
    ),
    passengers_age=[40],
    locale="en",
    currency="EUR",
)

_DEBERCBS_FRPARPGB = amqp_pb2.SearchCriteriaTask(
    offer_search_id="FOO",
    segments=[
        models_pb2.Segment(
            id="segment_id",
            legs=[
                models_pb2.Leg(
                    id="leg_id",
                    origin=models_pb2.Point(
                        time_zone="Europe/Berlin",
                    ),
                    destination=models_pb2.Point(
                        time_zone="Europe/Paris",
                    ),
                    departure_at=protobuf.datetime_to_protobuf(
                        datetime.datetime.combine(
                            protobuf.protobuf_to_date(
                                _DEBERCBS_FRPARPGB_CRITERIA.outbound_departure,
                            ),
                            datetime.time(
                                5,
                                17,
                                tzinfo=zoneinfo.ZoneInfo("Europe/Berlin"),
                            ),
                        ),
                    ),
                    arrival_at=protobuf.datetime_to_protobuf(
                        datetime.datetime.combine(
                            protobuf.protobuf_to_date(
                                _DEBERCBS_FRPARPGB_CRITERIA.outbound_departure,
                            ),
                            datetime.time(
                                21,
                                36,
                                tzinfo=zoneinfo.ZoneInfo("Europe/Paris"),
                            ),
                        ),
                    ),
                ),
            ],
        ),
    ],
    criteria=_DEBERCBS_FRPARPGB_CRITERIA,
)


@disable_by_default
async def test_search(
    distribusion_search_adapter: DistribusionSearchAdapter,
) -> None:
    search_results = distribusion_search_adapter.gather_search_results(
        distribusion_search_adapter.search_criteria_generator(_DEBERCBS_FRPARPGB),
    )
    count = 0

    async for offer in search_results:
        assert isinstance(offer, offer_models_pb2.OfferGroup)
        count = count + 1

    assert count > 0
