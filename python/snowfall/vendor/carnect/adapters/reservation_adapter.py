from snowfall.vendor.carnect.adapters.common import (
    BaseAdapter,
    get_error_text,
    get_warning_text,
)
from snowfall.vendor.carnect.models.service import (
    ServiceSoapGetVehReservationOutput,
    VehicleReservationType,
)


class ReservationAdapter(BaseAdapter):
    def __init__(self, envelop: ServiceSoapGetVehReservationOutput | None) -> None:
        self._envelop = envelop
        self._rs = envelop.body.veh_res_rs if envelop and envelop.body else None

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

    def get_id_context(self) -> str | None:
        reservation = self.reservation()

        if reservation and reservation.veh_segment_core:
            conf_ids = reservation.veh_segment_core.conf_id

            for conf_id in conf_ids:
                if conf_id.id_context is not None:
                    return conf_id.id_context
        return None

    def get_unique_id(self) -> str | None:
        reservation = self.reservation()

        if reservation and reservation.veh_segment_core:
            conf_ids = reservation.veh_segment_core.conf_id

            for conf_id in conf_ids:
                if conf_id.id:
                    return conf_id.id

        return None

    def reservation(self) -> VehicleReservationType | None:
        if self._rs and self._rs.veh_res_rscore:
            return self._rs.veh_res_rscore.veh_reservation

        return None
