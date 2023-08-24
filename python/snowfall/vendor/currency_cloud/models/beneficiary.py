from pydantic import v1 as pydantic

from snowfall.vendor.currency_cloud.models.base import CamelCaseBaseModel


class BeneficiaryValidate(CamelCaseBaseModel):
    bank_country: str
    currency: str
    beneficiary_company_name: str | None
    beneficiary_address: list[str] | None = None
    beneficiary_country: str | None = None
    account_number: str | None = None
    routing_code_type_1: str | None = None  # noqa: WPS114
    routing_code_value_1: str | None = None  # noqa: WPS114
    bic_swift: str | None = None
    iban: str | None = None
    bank_address: list[str] | None = None
    bank_name: str | None = None
    bank_account_type: str | None = None
    beneficiary_city: str | None = None
    beneficiary_postcode: str | None = None
    beneficiary_state_or_province: str | None = None
    payment_types: list[str] | None = None
    beneficiary_entity_type: str | None = "company"


class Beneficiary(BeneficiaryValidate):
    name: str | None
    bank_account_holder_name: str
    email: str | None = None


class BeneficiaryValidateRequest(BeneficiaryValidate):
    """Beneficiary validate pydantic request model."""


class BeneficiaryRequest(Beneficiary):
    """Beneficiary pydantic request model."""


class BeneficiaryValidateResponse(BeneficiaryValidate):
    identifier: str | None = pydantic.Field(None, alias="id")


class BeneficiaryResponse(Beneficiary):
    identifier: str = pydantic.Field(..., alias="id")
