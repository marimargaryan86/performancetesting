import type { ValidationError } from "$models/common-models";
import type { Currency } from "$models/finance-models";
import type { Country } from "$models/location-models";

export type BeneficiaryDetailsData = {
  nickname: string;
  addressCountry: Country;
  accountCountry: Country;
  accountCurrency: Currency;
};

export type BeneficiaryDetailsError = ValidationError<BeneficiaryDetailsData>;

export type PaymentTypeData = {
  paymentTypes: ("priority" | "regular")[];
  addressCountry: Country;
  addressLine: string;
  addressPostalCode: string;
};

export type PaymentTypeError = ValidationError<PaymentTypeData>;

export type PaymentOption = "swift" | "sort-code";

export type PaymentOptionsData = {
  paymentOptions: PaymentOption[];
  iban: string;
  bicSwift: string;
  sortCode: string;
};

export type PaymentOptionsError = ValidationError<PaymentOptionsData>;

export type CompanyDetailsData = {
  type: "company";
  companyName: string;
  companyRegistrationDate: Date;
};

export type IndividualDetailsData = {
  type: "individual";
  individualFirstName: string;
  individualLastName: string;
  individualBirthDate: Date;
};

export type EntityDetailsData = CompanyDetailsData | IndividualDetailsData;
export type CompanyDetailsError = ValidationError<CompanyDetailsData>;
export type IndividualDetailsError = ValidationError<IndividualDetailsData>;
export type EntityDetailsError = ValidationError<CompanyDetailsError & IndividualDetailsError>;

export type AccountDetailsData = {
  accountCurrency: Currency;
  accountCity: string;
  accountCountry: Country;
  accountHolderName: string;
  accountNumber: string;
};

export type AccountDetailsError = ValidationError<AccountDetailsData>;

export type BankAccountDetailsData = EntityDetailsData &
  AccountDetailsData &
  PaymentTypeData &
  PaymentOptionsData;

export type BankAccountDetailsError = ValidationError<BankAccountDetailsData>;

export type BeneficiaryData = BeneficiaryDetailsData & BankAccountDetailsData;

export type BeneficiaryError = ValidationError<BeneficiaryData>;
