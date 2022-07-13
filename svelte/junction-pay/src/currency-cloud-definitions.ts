export type PaymentType = "regular" | "priority";
export type RoutingCodeType2 =
  | "sort_code"
  | "aba"
  | "bsb_code"
  | "institution_no"
  | "bank_code"
  | "branch_code"
  | "clabe"
  | "cnaps";
export type RoutingCodeType1 = RoutingCodeType2 | "ifsc";
export type BankAccountType = "checkings" | "savings";
export type BeneficiaryEntityType = "individual" | "company";
export type BeneficiaryIdentificationType =
  | "none"
  | "drivers_license"
  | "social_security_number"
  | "green_card"
  | "passport"
  | "visa"
  | "matricula_consular"
  | "registro_federal_de_contribuyentes"
  | "clave_unica_de_registro_de_poblacion"
  | "credential_de_elector"
  | "social_insurance_number"
  | "citizenship_papers"
  | "drivers_license_canadian"
  | "existing_credit_card_details"
  | "employer_identification_number"
  | "national_id"
  | "incorporation_number"
  | "others";

export type BeneficiaryRequired = {
  name: string;
  bank_account_holder_name: string;
  bank_country: string;
  currency: string;
};

export type BeneficiaryOptional = Partial<{
  email: string;
  beneficiary_adress: string;
  account_number: string;
  routing_code_type_1: RoutingCodeType1;
  routing_code_value_1: string;
  routing_code_type_2: RoutingCodeType2;
  routing_code_value_2: string;
  bic_swift: string;
  iban: string;
  default_beneficiary: boolean;
  bank_address: string;
  bank_name: string;
  bank_account_type: BankAccountType;
  beneficiary_entity_type: BeneficiaryEntityType;
  beneficiary_city: string;
  beneficiary_postcode: string;
  beneficiary_state_or_province: string;
  beneficiary_date_of_birth: Date;
  beneficiary_identification_type: BeneficiaryIdentificationType;
  beneficiary_identification_value: string;
  payment_types: PaymentType[];
  on_behalf_of: string;
  beneficiary_external_reference: string;
}>;

export type BeneficiaryCompany = BeneficiaryRequired &
  BeneficiaryOptional & {
    beneficiary_company_name: string;
  };

export type BeneficiaryIndividual = BeneficiaryRequired &
  BeneficiaryOptional & {
    beneficiary_first_name: string;
    beneficiary_last_name: string;
  };
