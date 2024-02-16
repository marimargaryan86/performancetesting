from __future__ import annotations

import decimal

from snowfall.vendor.carnect import config
from snowfall.vendor.carnect.builders.common import (
    PersonNameTypeBuilder,
    PosBuilder,
    UniqueIdTypeBuilder,
)
from snowfall.vendor.carnect.models.service import (
    VehicleRetrieveResRqcoreType,
    VehRetResRq,
    VehRetResRqTarget,
)


class VehRetResRqBuilder(object):
    def __init__(self, conf: config.Config) -> None:
        self._rq = VehRetResRq()
        self._rq.version = decimal.Decimal("1.0")
        self._pos = PosBuilder()
        self._pos.set_credentials(conf)
        self._rq.pos = self._pos.get()
        self._rq.target = (
            VehRetResRqTarget.TEST if conf.is_test else VehRetResRqTarget.PRODUCTION
        )

    def build(self) -> VehRetResRq:
        return self._rq

    def pos(self) -> PosBuilder:
        return self._pos

    def unique_id(self) -> UniqueIdTypeBuilder:
        unique_id_builder = UniqueIdTypeBuilder()
        self._veh_ret_res_rqcore().unique_id = unique_id_builder.get()
        return unique_id_builder

    def person_name(self) -> PersonNameTypeBuilder:
        person_name = PersonNameTypeBuilder()
        self._veh_ret_res_rqcore().person_name = person_name.get()
        return person_name

    def surname(self, surname: str) -> None:
        if self._rq.veh_ret_res_rqcore and self._rq.veh_ret_res_rqcore.person_name:
            self._rq.veh_ret_res_rqcore.person_name.surname = surname

    def _veh_ret_res_rqcore(self) -> VehicleRetrieveResRqcoreType:
        if not self._rq.veh_ret_res_rqcore:
            self._rq.veh_ret_res_rqcore = VehicleRetrieveResRqcoreType()

        return self._rq.veh_ret_res_rqcore
