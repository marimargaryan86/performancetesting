import contextlib
import datetime

import more_itertools
from redis import exceptions

from snowfall.project.junction.go.service.offers.v1alpha import models_pb2 as offers_pb2
from snowfall.project.junction.go.v1alpha import models_pb2 as common_pb2
from snowfall.project.junction.provider import offers as provider_offers
from snowfall.project.junction.service.providers.mock import conftest, offers
from snowfall.stdlib import money
from snowfall.stdlib.format import protobuf


class TestResults(object):
    async def test_empty_trips_returns_no_results(
        self,
        searcher: provider_offers.TripOfferSearcher[offers.Criteria, offers.Criteria],
    ) -> None:
        offer_search = conftest.generate_offer_search(trips=0)
        offer_groups = await self._collect_offer_groups(searcher, offer_search)

        assert not offer_groups

    async def test_single_trip_gives_single_result(
        self,
        searcher: provider_offers.TripOfferSearcher[offers.Criteria, offers.Criteria],
    ) -> None:
        offer_search = conftest.generate_offer_search()
        offer_groups = await self._collect_offer_groups(searcher, offer_search)

        assert len(offer_groups) == 1

    async def test_multiple_trips_gives_multiple_results(
        self,
        searcher: provider_offers.TripOfferSearcher[offers.Criteria, offers.Criteria],
    ) -> None:
        offer_search = conftest.generate_offer_search(trips=2)
        offer_groups = await self._collect_offer_groups(searcher, offer_search)

        assert len(offer_groups) == 2

    async def test_multiple_segments_of_same_type_gives_single_result(
        self,
        searcher: provider_offers.TripOfferSearcher[offers.Criteria, offers.Criteria],
    ) -> None:
        offer_search = conftest.generate_offer_search(segments=2)
        offer_groups = await self._collect_offer_groups(searcher, offer_search)

        assert len(offer_groups) == 1

    async def test_multiple_segments_of_different_types_gives_multiple_results(
        self,
        searcher: provider_offers.TripOfferSearcher[offers.Criteria, offers.Criteria],
    ) -> None:
        offer_search = conftest.generate_offer_search(segments=2)
        segments = offer_search.trips[0].segments
        segments[1].legs[0].type = common_pb2.Schedule.TYPE_RAIL
        offer_groups = await self._collect_offer_groups(searcher, offer_search)

        assert len(offer_groups) == 2

    async def _collect_offer_groups(
        self,
        searcher: provider_offers.TripOfferSearcher[offers.Criteria, offers.Criteria],
        offer_search: offers_pb2.TripOfferSearch,
    ) -> list[offers_pb2.OfferGroup]:
        offer_groups = []

        # This happens for some reason when collecting more than one result.
        with contextlib.suppress(exceptions.NoScriptError):
            async for offer_group in searcher.search(offer_search):
                offer_groups.append(offer_group)

        return offer_groups


class TestOfferGroupModel(object):
    def test_has_id(self, offer_group: offers_pb2.OfferGroup) -> None:
        assert offer_group.id

    def test_has_expiry(self, offer_group: offers_pb2.OfferGroup) -> None:
        now = datetime.datetime.now(tz=datetime.UTC)
        assert protobuf.protobuf_to_datetime(offer_group.expires_at) > now

    def test_has_offers(self, offer_group: offers_pb2.OfferGroup) -> None:
        assert offer_group.offers

    def test_has_segments(self, offer_group: offers_pb2.OfferGroup) -> None:
        assert offer_group.segments


class TestOfferSegmentModel(object):
    def test_has_id(self, offer_segment: offers_pb2.OfferSegment) -> None:
        assert offer_segment.id

    def test_has_segment_id(
        self,
        offer_segment: offers_pb2.OfferSegment,
        search_segment: common_pb2.Segment,
    ) -> None:
        assert offer_segment.segment_id == search_segment.id

    def test_has_operator(self, offer_segment: offers_pb2.OfferSegment) -> None:
        assert offer_segment.operator

    def test_has_vendor(self, offer_segment: offers_pb2.OfferSegment) -> None:
        assert offer_segment.vendor

    def test_has_type(
        self,
        offer_segment: offers_pb2.OfferSegment,
        search_segment: common_pb2.Segment,
    ) -> None:
        assert offer_segment.type == more_itertools.first(search_segment.legs).type

    def test_has_vehicle(self, offer_segment: offers_pb2.OfferSegment) -> None:
        assert offer_segment.vehicle.number


class TestOfferSegmentLegModel(object):
    def test_has_id(self, offer_segment_leg: offers_pb2.OfferSegmentLeg) -> None:
        assert offer_segment_leg.id

    def test_has_origin(
        self,
        offer_segment_leg: offers_pb2.OfferSegmentLeg,
        search_leg: common_pb2.Leg,
    ) -> None:
        assert (
            offer_segment_leg.origin.SerializeToString()
            == search_leg.origin.SerializeToString()
        )

    def test_has_destination(
        self,
        offer_segment_leg: offers_pb2.OfferSegmentLeg,
        search_leg: common_pb2.Leg,
    ) -> None:
        assert (
            offer_segment_leg.destination.SerializeToString()
            == search_leg.destination.SerializeToString()
        )

    def test_has_departure_at(
        self,
        offer_segment_leg: offers_pb2.OfferSegmentLeg,
        search_leg: common_pb2.Leg,
    ) -> None:
        assert (
            offer_segment_leg.departure_at.SerializeToString()
            == search_leg.departure_at.SerializeToString()
        )

    def test_has_arrival_at(
        self,
        offer_segment_leg: offers_pb2.OfferSegmentLeg,
        search_leg: common_pb2.Leg,
    ) -> None:
        assert (
            offer_segment_leg.arrival_at.SerializeToString()
            == search_leg.arrival_at.SerializeToString()
        )


class TestOfferOptionModel(object):
    def test_has_id(self, offer_option: offers_pb2.Offer) -> None:
        assert offer_option.id

    def test_has_price(self, offer_option: offers_pb2.Offer) -> None:
        amount = money.from_protobuf(offer_option.price)

        assert amount.amount

    def test_has_brand_name(self, offer_option: offers_pb2.Offer) -> None:
        assert offer_option.brand_name == offers.BRAND_NAME


class TestOfferSegmentDetails(object):
    def test_has_id(
        self,
        offer_segment_details: offers_pb2.OfferSegmentDetails,
    ) -> None:
        assert offer_segment_details.id

    def test_has_offer_segment_id(
        self,
        offer_segment_details: offers_pb2.OfferSegmentDetails,
        offer_segment: offers_pb2.OfferSegment,
    ) -> None:
        assert offer_segment_details.offer_segment_id == offer_segment.id

    def test_has_cabin_class(
        self,
        offer_segment_details: offers_pb2.OfferSegmentDetails,
    ) -> None:
        assert offer_segment_details.cabin_class.marketing_name
        assert (
            offer_segment_details.cabin_class.type
            != common_pb2.CabinClass.TYPE_UNSPECIFIED
        )
