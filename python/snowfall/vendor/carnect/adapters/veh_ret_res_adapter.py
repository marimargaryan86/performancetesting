from snowfall.vendor.carnect.adapters.common import (
    BaseAdapter,
    get_error_text,
    get_warning_text,
)
from snowfall.vendor.carnect.models.service import (
    ServiceSoapGetVehRetReservationOutput,
    VehicleRetrieveResRscoreType,
)


class VehRetResAdapter(BaseAdapter):
    def __init__(self, envelop: ServiceSoapGetVehRetReservationOutput | None) -> None:
        self._envelop = envelop
        self._rs = envelop.body.veh_ret_res_rs if envelop and envelop.body else None

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

    def rs_core(self) -> VehicleRetrieveResRscoreType | None:
        if self._rs and self._rs.veh_ret_res_rscore:
            return self._rs.veh_ret_res_rscore

        return None
