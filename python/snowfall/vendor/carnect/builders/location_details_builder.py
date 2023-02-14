from snowfall.vendor.carnect import config
from snowfall.vendor.carnect.builders.common import PosBuilder
from snowfall.vendor.carnect.models.service import VehLocDetailRq, VehLocDetailRqTarget


class LocationDetailsRqBuilder(object):
    def __init__(self, conf: config.Config) -> None:
        self._rq = VehLocDetailRq()
        self._pos = PosBuilder()
        self._pos.set_credentials(conf)
        self._rq.pos = self._pos.get()
        self._rq.target = (
            VehLocDetailRqTarget.TEST
            if conf.target == "TEST"
            else VehLocDetailRqTarget.PRODUCTION
        )

    def build(self) -> VehLocDetailRq:
        return self._rq

    def target(self, target: VehLocDetailRqTarget) -> None:
        self._rq.target = target

    def pos(self) -> PosBuilder:
        return self._pos

    def location_code(self, location_code: str) -> None:
        self._rq.location = VehLocDetailRq.Location(
            code_context="1",
            location_code=location_code,
        )

    def extended_location_code(self, extended_location_code: str) -> None:
        self._rq.location = VehLocDetailRq.Location(
            code_context="2",
            extended_location_code=extended_location_code,
        )
