import type { OrderDirection } from "./common";

export const routingCodeTypes = [
  "sort_code",
  "aba",
  "bsb_code",
  "institution_no",
  "bank_code",
  "branch_code",
  "clabe",
  "cnaps",
  "ifsc",
] as const;

export type RoutingCodeType = typeof routingCodeTypes[number];

export const bankAccountTypes = ["savings", "checking"] as const;

export type BankAccountType = typeof bankAccountTypes[number];

export const entityTypes = ["individual", "company"] as const;

export type EntityType = typeof entityTypes[number];

export const identificationTypes = [
  "none",
  "drivers_license",
  "social_security_number",
  "green_card",
  "passport",
  "visa",
  "matricula_consular",
  "registro_federal_de_contribuyentes",
  "clave_unica_de_registro_de_poblacion",
  "credential_de_elector",
  "social_insurance_number",
  "citizenship_papers",
  "drivers_license_canadian",
  "existing_credit_card_details",
  "employer_identification_number",
  "national_id",
  "incorporation_number",
  "others",
] as const;

export type IdentificationType = typeof identificationTypes[number];

export const paymentTypes = ["regular", "priority"] as const;

export type PaymentType = typeof paymentTypes[number];

export const scopeTypes = ["own", "clients", "all"] as const;

export type ScopeType = typeof scopeTypes[number];

export type BeneficiaryRequiredSchema = {
  bank_account_holder_name: string;
  name: string;
  currency: string;
  bank_country: string;
};

export type BeneficiaryOptionalSchema = {
  default_beneficiary: string;
  email: string | null;
  beneficiary_country: string | null;
  account_number: string | null;
  routing_code_type_1: RoutingCodeType | null;
  routing_code_value_1: string | null;
  routing_code_type_2: RoutingCodeType | null;
  routing_code_value_2: string | null;
  bic_swift: string | null;
  iban: string | null;
  bank_name: string | null;
  bank_account_type: BankAccountType | null;
  beneficiary_entity_type: EntityType | null;
  beneficiary_company_name: string | null;
  beneficiary_first_name: string | null;
  beneficiary_last_name: string | null;
  beneficiary_city: string | null;
  beneficiary_postcode: string | null;
  beneficiary_state_or_province: string | null;
  beneficiary_date_of_birth: string | null;
  beneficiary_identification_type: IdentificationType | null;
  beneficiary_identification_value: string | null;
  beneficiary_external_reference: string | null;
};

export type BeneficiaryPutSchema = BeneficiaryRequiredSchema &
  Partial<
    BeneficiaryOptionalSchema & {
      "payment_types[]": PaymentType[];
      on_behalf_of: string | null;
      bank_address: string | null;
      beneficiary_address: string | null;
    }
  >;

export type BeneficiarySchema = BeneficiaryRequiredSchema &
  BeneficiaryOptionalSchema & {
    id: string;
    payment_types: PaymentType[];
    created_at: string;
    updated_at: string;
    creator_contact_id: string;
    bank_address: string[];
    beneficiary_address: string[];
  };

export type GetRequirementsSchema = {
  currency: string;
  bank_account_country: string;
  beneficiary_country?: string;
};

export type RequirementsSchema = {
  payment_type: PaymentType;
  beneficiary_entity_type: EntityType;
  beneficiary_address?: string;
  beneficiary_city?: string;
  beneficiary_country?: string;
  beneficiary_first_name?: string;
  beneficiary_last_name?: string;
  beneficiary_company_name?: string;
  beneficiary_postcode?: string;
  beneficiary_state_or_province?: string;
  acct_number?: string;
  sort_code?: string;
  iban?: string;
  bic_swift?: string;
};

export type RequirementsResponseSchema = {
  details: RequirementsSchema[];
};

export const orderFields = [
  "bank_account_holder_name",
  "beneficiary_country",
  "currency",
  "account_number",
  "bic_swift",
  "iban",
  "default_beneficiary",
  "bank_account_type",
  "name",
] as const;

export type OrderField = typeof orderFields[number];

export type FindCriteriaSchema = {
  on_behalf_of?: string;
  bank_account_holder_name?: string;
  beneficiary_country?: string;
  currency?: string;
  account_number?: string;
  "routing_code_type[0]"?: RoutingCodeType;
  "routing_code_value[0]"?: string;
  bic_swift?: string;
  iban?: string;
  default_beneficiary?: string;
  bank_name?: string;
  bank_account_type?: BankAccountType;
  name?: string;
  beneficiary_entity_type?: EntityType;
  beneficiary_company_name?: string;
  beneficiary_first_name?: string;
  beneficiary_last_name?: string;
  beneficiary_city?: string;
  beneficiary_postcode?: string;
  beneficiary_state_or_province?: string;
  beneficiary_date_of_birth?: string;
  beneficiary_external_reference?: string;
  scope?: ScopeType;
  page?: number;
  per_page?: number;
  order?: OrderField;
  order_asc_desc?: OrderDirection;
};

export type FindBeneficiariesResponseSchema = {
  beneficiaries: BeneficiarySchema[];
};
