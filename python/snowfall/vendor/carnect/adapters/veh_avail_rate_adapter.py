from typing import List

from snowfall.vendor.carnect.adapters.common import (
    BaseAdapter,
    get_error_text,
    get_warning_text,
)
from snowfall.vendor.carnect.models.service import (
    ServiceSoapGetVehAvailRateOutput,
    VehicleVendorAvailabilityType,
)


class VehAvailRateAdapter(BaseAdapter):
    def __init__(self, envelop: ServiceSoapGetVehAvailRateOutput | None) -> None:
        self._envelop = envelop
        self._rs = envelop.body.veh_avail_rate_rs if envelop and envelop.body else None

    def is_success(self) -> bool:
        return (
            self._envelop is not None
            and self._envelop.header is not None
            and self._envelop.header.information_header is not None
            and self._envelop.header.information_header.successfully is True
        )

    def get_error(self) -> str | None:
        return get_error_text(self._rs.errors) if self._rs else None

    def get_warning(self) -> str | None:
        return get_warning_text(self._rs.warnings) if self._rs else None

    def available(self) -> List[VehicleVendorAvailabilityType]:
        if (  # noqa: WPS337
            self._rs
            and self._rs.veh_avail_rscore
            and self._rs.veh_avail_rscore.veh_vendor_avails
            and self._rs.veh_avail_rscore.veh_vendor_avails.veh_vendor_avail
        ):
            return self._rs.veh_avail_rscore.veh_vendor_avails.veh_vendor_avail

        return []
