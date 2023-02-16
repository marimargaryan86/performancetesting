from __future__ import annotations

from datetime import datetime

from pydantic.types import Decimal

from snowfall.vendor.carnect.builders.common import PosBuilder
from snowfall.vendor.carnect.config import Config
from snowfall.vendor.carnect.models.service import (
    ArrayOfVehicleAvailRqcoreTypeVehPref,
    RateQueryType,
    VehAvailRateRq,
    VehAvailRateRqTarget,
    VehicleAvailRqcoreType,
    VehicleRentalCoreType,
)
from snowfall.vendor.carnect.xml_datetime_tools import datetime_to_xml


class VehicleRentalCoreBuilder(object):  # noqa: WPS214
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

    def add_pick_up_iata(self, iata: str) -> VehicleRentalCoreBuilder:
        self.add_pick_up_location(iata, "2")
        return self

    def add_pick_up_city_id(self, city_id: str) -> VehicleRentalCoreBuilder:
        self.add_pick_up_location(city_id, "1")
        return self

    def add_pick_up_geo_coords(self, geo_coords: str) -> VehicleRentalCoreBuilder:
        self.add_pick_up_location(geo_coords, "3")
        return self

    def return_location_iata(self, iata: str) -> VehicleRentalCoreBuilder:
        self.return_location(iata, "2")
        return self

    def return_location_city_id(self, city_id: str) -> VehicleRentalCoreBuilder:
        self.return_location(city_id, "1")
        return self

    def return_geo_coords(self, geo_coords: str) -> VehicleRentalCoreBuilder:
        self.return_location(geo_coords, "3")
        return self


class VehAvailRateRqBuilder(object):  # noqa: WPS214
    def __init__(self, config: Config) -> None:
        self._rq = VehAvailRateRq()
        self._rq.version = Decimal("1.0")
        self._pos = PosBuilder()
        self._pos.set_credentials(config)
        self._rq.pos = self._pos.get()
        self._rq.target = (
            VehAvailRateRqTarget.TEST
            if config.is_test
            else VehAvailRateRqTarget.PRODUCTION
        )

    def build(self) -> VehAvailRateRq:
        return self._rq

    def pos(self) -> PosBuilder:
        return self._pos

    def version(self, version: str = "large") -> VehAvailRateRqBuilder:
        self._rq.req_resp_version = version
        return self

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

    def add_driver_age(self, age: int) -> VehAvailRateRqBuilder:
        driver = VehicleAvailRqcoreType.DriverType()
        driver.age = age
        self._veh_avail_rqcore().driver_type.append(driver)
        return self

    def add_pref_vendor(self, vendor_code: str) -> VehAvailRateRqBuilder:
        vendor = ArrayOfVehicleAvailRqcoreTypeVehPref.VehPref()
        vendor.code = vendor_code
        self._vendor_pref().append(vendor)
        return self

    def _vendor_pref(self) -> list[ArrayOfVehicleAvailRqcoreTypeVehPref.VehPref]:
        rq_core = self._veh_avail_rqcore()

        if not rq_core.veh_prefs:
            rq_core.veh_prefs = ArrayOfVehicleAvailRqcoreTypeVehPref()

        return rq_core.veh_prefs.veh_pref

    def _veh_avail_rqcore(self) -> VehicleAvailRqcoreType:
        if not self._rq.veh_avail_rqcore:
            self._rq.veh_avail_rqcore = VehicleAvailRqcoreType()

        return self._rq.veh_avail_rqcore
