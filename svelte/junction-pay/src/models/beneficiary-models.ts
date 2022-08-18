export type BeneficiaryType = "company" | "individual";
export type PaymentTypes = "regular" | "priority";
export type Options = "sort_code" | "swift";

export type Country = {
  currencyCode: string;
  name: string;
};

export type Currency = {
  code: string;
};

export type AddBeneficiaryDetailsData = {
  nickname: string;
  beneficiaryCountry: Country;
  bankAccountCountry: Country;
  currency: Currency;
};

export type AddBeneficiaryBankData = {
  beneficiaryEntityType: BeneficiaryType;
  beneficiaryDateOfBirth: Date;
  paymentTypes: PaymentTypes[];
  options: string[];
};

export type BeneficiaryIdentity = {
  beneficiaryEntityType: "";
  beneficiaryFirstName?: string;
  beneficiaryLastName?: string;
  beneficiaryEntityName?: string;
};

export type IndividualBeneficiary = AddBeneficiaryBankData & {
  beneficiaryEntityType: "individual";
  beneficiaryFirstName: string;
  beneficiaryLastName: string;
};

export type CompanyBeneficiary = AddBeneficiaryBankData & {
  beneficiaryEntityType: "company";
  beneficiaryEntityName: string;
};

export type AccountDetails = {
  accountName: string;
  accountNumber: number;
};

export type BeneficiaryAddress = {
  addressLine: string;
  postCode: string;
};

export type SortBankDetails = {
  sortCode: string;
};

export type IBANBankDetails = {
  bic: string;
  iban: string;
};

export type AddBeneficiaryBankDetails = IndividualBeneficiary | CompanyBeneficiary;

export type AddBeneficiaryBankDetailsCombined = AddBeneficiaryBankDetails &
  AccountDetails &
  BeneficiaryAddress &
  SortBankDetails &
  IBANBankDetails;

export type AddBeneficiaryBankDetailsIndividual = AddBeneficiaryBankData &
  IndividualBeneficiary &
  AccountDetails &
  BeneficiaryAddress &
  SortBankDetails &
  IBANBankDetails;

export type AddBeneficiaryBankDetailsCompany = AddBeneficiaryBankData &
  CompanyBeneficiary &
  AccountDetails &
  BeneficiaryAddress &
  SortBankDetails &
  IBANBankDetails;

export type BeneficiaryWizardComplete = AddBeneficiaryBankDetailsCombined &
  AddBeneficiaryDetailsData;

export type CCBeneficiaryModel = {
  beneficiary_entity_type: BeneficiaryType;
  beneficiary_company_name: string;
  bank_account_holder_name: string;
  beneficiary_first_name: string;
  beneficiary_last_name: string;
  beneficiary_address: string;
  beneficiary_city: string;
  beneficiary_country: string;
  iban: string;
  bic_swift: string;
  id: string;
};
