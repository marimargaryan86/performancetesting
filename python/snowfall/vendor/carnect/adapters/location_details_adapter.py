from snowfall.vendor.carnect.adapters.common import (
    BaseAdapter,
    get_error_text,
    get_warning_text,
)
from snowfall.vendor.carnect.models.service import (
    ServiceSoapGetVehLocDetailOutput,
    VehicleLocationDetailsType,
)


class LocationDetailsAdapter(BaseAdapter):
    def __init__(self, envelop: ServiceSoapGetVehLocDetailOutput | None) -> None:
        self._envelop = envelop
        self._rs = envelop.body.veh_loc_detail_rs if envelop and envelop.body else None

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

    def location_details(self) -> VehicleLocationDetailsType | None:
        if self._rs and self._rs.location_detail:
            return self._rs.location_detail

        return None
