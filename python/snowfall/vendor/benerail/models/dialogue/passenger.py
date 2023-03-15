from datetime import date

from pydantic import AnyUrl, ConstrainedStr, Field

from snowfall.vendor.benerail.models.base import BenerailBaseModel
from snowfall.vendor.benerail.models.dialogue.enums import Gender, PassengerStatus
from snowfall.vendor.benerail.models.link import Supplier
from snowfall.vendor.benerail.models.regex import NumberRegex, URNRegex

_FCE_LENGTH = 20

_CONTRACT_NR_LENGTH = 12


class ReductionCardURN(BenerailBaseModel):
    __root__: ConstrainedStr = Field(
        ...,
        example="urn:bnds:reduction_card:FF",
        regex="^urn:[a-z]*:(ftp_card_types|reduction_card):[A-Z_0-9]*$",
    )


class ReductionCard(BenerailBaseModel):
    href: AnyUrl | None = Field(
        None,
        example="https://api.example.com/places/urn:bnds:reduction_card:RAP",
    )
    card_value: ReductionCardURN | None = Field(None, alias="value")


class PassengerRequestCards(BenerailBaseModel):
    card_type: ReductionCardURN = Field(..., alias="type")
    number: str | None = Field(
        None,
        description="individual card number",
        example="125548-95687",
    )


class PassengerCards(BenerailBaseModel):
    passenger_cards_type: ReductionCard | None = Field(None, alias="type")
    number: str | None = Field(
        None,
        description="individual card number",
        example="125548-95687",
    )


class PassengerRequestCorporateContracts(BenerailBaseModel):
    contract_nr: NumberRegex = Field(
        ...,
        example="04-0608",
        max_length=_CONTRACT_NR_LENGTH,
    )
    supplier: URNRegex = Field(..., example="urn:itti:supplier:ICE")
    fce: ConstrainedStr | None = Field(None, example="C0058U2", max_length=_FCE_LENGTH)


class PassengerCorporateContracts(BenerailBaseModel):
    contract_nr: str | None = None
    supplier: Supplier | None = None
    fce: str | None = None


class PassengerDetail(BenerailBaseModel):
    preferred_language: str | None = Field(
        None,
        description="Languages spoken by the traveler (ISO Language code)",
        example="EN",
    )
    title: str | None = Field(None, description="(Formal) title", example="Mr.")
    first_name: str | None = Field(None, example="John")
    last_name: str | None = Field(None, example="Massis")
    email: str | None = Field(None, example="john.massis@example.com")
    phone_number: str | None = Field(
        None,
        description="Preferably a mobile phone number",
    )


class PassengerRequest(BenerailBaseModel):
    external_reference: str | None = Field(
        None,
        description="For consumer use. Field will not be evaluated.",
        example="PA123456",
    )
    date_of_birth: date | None = Field(
        None,
        description="Use ISO-6801 standard. Date only no time.",
        example="1999-08-11",
    )
    cards: list[PassengerRequestCards] | None = None
    corporate_contracts: list[PassengerRequestCorporateContracts] | None = None
    gender: Gender | None = None
    details: PassengerDetail | None = None


class Passenger(BenerailBaseModel):
    identifier: str | None = Field(None, alias="id")
    external_reference: str | None = Field(
        None,
        description="For consumer use. Field will not be evaluated.",
        example="PA123456",
    )
    date_of_birth: date | None = Field(
        None,
        description="Use ISO-6801 standard. Date only no time.",
        example="1999-08-11",
    )
    cards: list[PassengerCards] | None = Field(
        None,
        description="reduction or loyalty cards owned by the passenger",
    )
    corporate_contracts: list[PassengerCorporateContracts] | None = None
    gender: Gender | None = None
    details: PassengerDetail | None = None
    passenger_status: PassengerStatus | None = None
