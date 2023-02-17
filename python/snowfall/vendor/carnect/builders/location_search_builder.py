from __future__ import annotations

from snowfall.vendor.carnect import config
from snowfall.vendor.carnect.builders.common import BaseBuilderRq, PosBuilder
from snowfall.vendor.carnect.models.service import (
    ItemSearchCriterionType,
    VehLocationSearchRq,
    VehLocationSearchRqTarget,
)


class VehLocSearchCriterionBuilder(object):
    def __init__(self) -> None:
        self._criterion = ItemSearchCriterionType()

    def get(self) -> ItemSearchCriterionType:
        return self._criterion

    def add_geo_point(self, latitude: float, longitude: float) -> None:
        self._criterion.position = ItemSearchCriterionType.Position(
            latitude=str(latitude),
            longitude=str(longitude),
        )
        self._criterion.ref_point.append(
            ItemSearchCriterionType.RefPoint(ref_point_type="8"),
        )

    def radius_km(self, radius_km: int) -> None:
        self._criterion.radius = ItemSearchCriterionType.Radius(
            distance_max=str(radius_km),
            distance_measure="km",
        )

    def ranking(self, ranking: int) -> None:
        self._criterion.ranking = ranking


class LocationSearchRqBuilder(BaseBuilderRq[VehLocationSearchRq]):
    def __init__(self, conf: config.Config) -> None:
        self._rq = VehLocationSearchRq()
        self._pos = PosBuilder()
        self._pos.set_credentials(conf)
        self._rq.pos = self._pos.get()
        self._rq.target = (
            VehLocationSearchRqTarget.TEST
            if conf.is_test
            else VehLocationSearchRqTarget.PRODUCTION
        )

    def build(self) -> VehLocationSearchRq:
        return self._rq

    def echo_token(self, echo_token: str) -> None:
        self._rq.echo_token = echo_token

    def pos(self) -> PosBuilder:
        return self._pos

    def add_search_criterion(self) -> VehLocSearchCriterionBuilder:
        criterion = VehLocSearchCriterionBuilder()
        self._rq.veh_loc_search_criterion.append(criterion.get())
        return criterion
