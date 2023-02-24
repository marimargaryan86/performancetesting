from decimal import Decimal

from snowfall.vendor.carnect.adapters.common import (
    BaseAdapter,
    get_error_text,
    get_warning_text,
)
from snowfall.vendor.carnect.models.service import (
    ServiceSoapGetVehRateRuleOutput,
    VehicleEquipmentPricedType,
    VehRateRuleRs,
)


class PricedEquipmentAdapter(object):
    def __init__(self, priced_equip: VehicleEquipmentPricedType) -> None:
        self._adapter: VehicleEquipmentPricedType = priced_equip

    def equipment_type(self) -> str | None:
        if self._adapter.equipment:
            return self._adapter.equipment.equip_type

        return None

    def description(self) -> str | None:
        if self._adapter.equipment:
            return self._adapter.equipment.description

        return None

    def charge_currency(self) -> str | None:
        if self._adapter.charge:
            return self._adapter.charge.currency_code

        return None

    def charge_amount(self) -> Decimal | None:
        if self._adapter.charge:
            return self._adapter.charge.amount

        return None


class VehRateRuleAdapter(BaseAdapter):
    def __init__(self, envelop: ServiceSoapGetVehRateRuleOutput | None) -> None:
        self._envelop = envelop
        self._rs = envelop.body.veh_rate_rule_rs if envelop and envelop.body else None
        self._priced_equipments: list[PricedEquipmentAdapter] = []

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

    def rate_rules(self) -> VehRateRuleRs.RateRules | None:
        if self._rs and self._rs.rate_rules:
            return self._rs.rate_rules

        return None

    def priced_equipments(self) -> list[PricedEquipmentAdapter]:
        if self._rs and self._rs.priced_equips and not self._priced_equipments:
            for priced_equip in self._rs.priced_equips.priced_equip:
                self._priced_equipments.append(PricedEquipmentAdapter(priced_equip))

        return self._priced_equipments
