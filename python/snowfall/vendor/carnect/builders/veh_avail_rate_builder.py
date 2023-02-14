from __future__ import annotations

from datetime import datetime

from pydantic.types import Decimal

from snowfall.vendor.carnect.builders.common import PosBuilder
from snowfall.vendor.carnect.models.service import (
    RateQueryType,
    VehAvailRateRq,
    VehicleAvailRqcoreType,
    VehicleRentalCoreType,
)
from snowfall.vendor.carnect.xml_datetime_tools import datetime_to_xml


class VehicleRentalCoreBuilder(object):
    def __init__(self) -> None:
        self._core_type = VehicleRentalCoreType()

    def get(self) -> VehicleRentalCoreType:
        return self._core_type

    def pick_up_date(self, date_time: datetime) -> VehicleRentalCoreBuilder:
        self._core_type.pick_up_date_time = datetime_to_xml(date_time)
        return self

    def return_date(self, date_time: datetime) -> VehicleRentalCoreBuilder:
        self._core_type.return_date_time = datetime_to_xml(date_time)
        return self

    def add_pick_up_location(
        self,
        location: str,
        code: str,
    ) -> VehicleRentalCoreBuilder:
        loc = VehicleRentalCoreType.PickUpLocation()
        loc.location_code = location
        loc.code_context = code
        self._core_type.pick_up_location.append(loc)
        return self

    def return_location(self, location: str, code: str) -> VehicleRentalCoreBuilder:
        self._core_type.return_location = VehicleRentalCoreType.ReturnLocation()
        self._core_type.return_location.location_code = location
        self._core_type.return_location.code_context = code
        return self


class VehAvailRateRqBuilder(object):
    def __init__(self) -> None:
        self._rq = VehAvailRateRq()
        self._rq.version = Decimal("1.0")
        self._rq.req_resp_version = "large"
        self._pos = PosBuilder()
        self._rq.pos = self._pos.get()

    def build(self) -> VehAvailRateRq:
        return self._rq

    def pos(self) -> PosBuilder:
        return self._pos

    def rate_query_parameter_type(self, param_type: str) -> VehAvailRateRqBuilder:
        self._veh_avail_rqcore().rate_query_parameter_type = param_type
        return self

    def rate_query_type(self, param_type: RateQueryType) -> VehAvailRateRqBuilder:
        self._veh_avail_rqcore().rate_query_type = param_type
        return self

    def get_rental_core(self) -> VehicleRentalCoreBuilder:
        rental_core = VehicleRentalCoreBuilder()
        self._veh_avail_rqcore().veh_rental_core = rental_core.get()
        return rental_core

    def _veh_avail_rqcore(self) -> VehicleAvailRqcoreType:
        if not self._rq.veh_avail_rqcore:
            self._rq.veh_avail_rqcore = VehicleAvailRqcoreType()

        return self._rq.veh_avail_rqcore
