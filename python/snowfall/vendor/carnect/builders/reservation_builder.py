from __future__ import annotations

import datetime
from typing import Generic, TypeVar

from snowfall.vendor.carnect.builders.common import (
    AddressInfoBuilder,
    BaseBuilderRq,
    PosBuilder,
)
from snowfall.vendor.carnect.config import Config
from snowfall.vendor.carnect.models.service import (
    CompanyNameType,
    CustomerPrimaryAdditionalType,
    CustomerType,
    CustomerTypeGender,
    EmailType,
    PersonNameType,
    UniqueIdType,
    VehicleArrivalDetailsType,
    VehiclePrefType,
    VehicleReservationRqcoreType,
    VehicleReservationRqcoreTypeSpecialEquipPrefsSpecialEquipPref,
    VehResRq,
    VehResRqTarget,
)
from snowfall.vendor.carnect.xml_datetime_tools import date_to_xml

ADDITIONAL_DRIVER_EQUIP_TYPE = "222"
C = TypeVar("C", bound=CustomerType)  # noqa: WPS111


class AddressBuilder(AddressInfoBuilder[CustomerType.Address]):
    def __init__(self) -> None:
        super().__init__(CustomerType.Address())


class CustomerBuilder(Generic[C]):
    def __init__(self, customer: C) -> None:
        self._customer = customer

    def get(self) -> C:
        return self._customer

    def given_name(self, given_name: str) -> None:
        self._person_name().given_name = [given_name]

    def surname(self, surname: str) -> None:
        self._person_name().surname = surname

    def gender(self, gender: CustomerTypeGender) -> None:
        self._customer.gender = gender

    def birth_date(self, birth_date: datetime.date) -> None:
        self._customer.birth_date = date_to_xml(birth_date)

    def language(self, language_code: str) -> None:
        self._customer.language = language_code

    def add_phone(
        self,
        phone_number: str,
        phone_type: str | None = "1",
    ) -> None:
        telephone = CustomerType.Telephone(
            phone_number=phone_number,
            phone_tech_type=phone_type,
        )
        self._customer.telephone.append(telephone)

    def add_email(self, email: str) -> None:
        self._customer.email.append(EmailType(value=email))

    def email(self, email: str) -> None:
        email_obj = EmailType(value=email)

        if self._customer.email:
            self._customer.email[0] = email_obj
        else:
            self._customer.email.append(email_obj)

    def citizen_country_code(self, citizen_country_code: str) -> None:
        self._customer.citizen_country_name = [
            CustomerType.CitizenCountryName(code=citizen_country_code),
        ]

    def add_address(self) -> AddressBuilder:
        address_builder = AddressBuilder()
        self._customer.address.append(address_builder.get())
        return address_builder

    def _person_name(self) -> PersonNameType:
        if self._customer.person_name is None:
            self._customer.person_name = PersonNameType()

        return self._customer.person_name


class CustomerPrimaryBuilder(CustomerBuilder[CustomerPrimaryAdditionalType.Primary]):
    def __init__(self) -> None:
        super().__init__(customer=CustomerPrimaryAdditionalType.Primary())


class CustomerAdditionalBuilder(
    CustomerBuilder[CustomerPrimaryAdditionalType.Additional],
):
    def __init__(self) -> None:
        super().__init__(customer=CustomerPrimaryAdditionalType.Additional())


class ReservationBuilder(BaseBuilderRq[VehResRq]):
    def __init__(self, config: Config) -> None:
        self._rq = VehResRq()
        self._pos = PosBuilder()
        self._rq.pos = self._pos.get()
        self._pos.set_credentials(config)
        self._veh_res_rqcore = VehResRq.VehResRqcore()
        self._rq.veh_res_rqcore = self._veh_res_rqcore
        self.target(
            VehResRqTarget.TEST if config.is_test else VehResRqTarget.PRODUCTION,
        )
        self._customer_primary: CustomerPrimaryBuilder | None = None

    def build(self) -> VehResRq:
        return self._rq

    def target(self, target: VehResRqTarget) -> None:
        self._rq.target = target

    def pos(self) -> PosBuilder:
        return self._pos

    def add_reservation_unique_id(self, unique_id: str) -> None:
        self._veh_res_rqcore.unique_id.append(
            UniqueIdType(id_context=unique_id, type="14"),
        )

    def veh_pref_code(self, veh_pref_code: str) -> None:
        # Code which is returned after price verification.
        # (value of ID_Context of VehAvailRateRS)

        if self._veh_res_rqcore.veh_pref is None:
            self._veh_res_rqcore.veh_pref = VehiclePrefType()

        self._veh_res_rqcore.veh_pref.code = veh_pref_code

    def add_equip_pref(self, equip_type: str, quantity: int = 1) -> None:
        pref = VehicleReservationRqcoreTypeSpecialEquipPrefsSpecialEquipPref(
            equip_type=equip_type,
            quantity=quantity,
        )

        if self._veh_res_rqcore.special_equip_prefs is None:
            self._veh_res_rqcore.special_equip_prefs = (
                VehicleReservationRqcoreType.SpecialEquipPrefs()
            )

        self._veh_res_rqcore.special_equip_prefs.special_equip_pref.append(pref)

    def arrival_flight(self, airline_code: str, flight_number: str) -> None:
        if self._rq.veh_res_rqinfo is None:
            self._rq.veh_res_rqinfo = VehResRq.VehResRqinfo()

        self._rq.veh_res_rqinfo.arrival_details = VehicleArrivalDetailsType(
            # TransportationCode=14 indicates plane,
            # as given by the OTA Transportation Code table
            transportation_code="14",
            number=flight_number,
            marketing_company=CompanyNameType(code=airline_code),
        )

    def primary_driver(self) -> CustomerPrimaryBuilder:
        if self._customer_primary is None:
            self._customer_primary = CustomerPrimaryBuilder()
            self._customer().primary = self._customer_primary.get()

        return self._customer_primary

    def add_additional_driver(self) -> CustomerAdditionalBuilder:
        customer_builder = CustomerAdditionalBuilder()
        self._customer().additional.append(customer_builder.get())
        return customer_builder

    def add_additional_driver_equip_pref(self) -> None:
        self.add_equip_pref(equip_type=ADDITIONAL_DRIVER_EQUIP_TYPE)

    def _customer(self) -> CustomerPrimaryAdditionalType:
        if self._veh_res_rqcore.customer is None:
            self._veh_res_rqcore.customer = CustomerPrimaryAdditionalType()

        return self._veh_res_rqcore.customer
