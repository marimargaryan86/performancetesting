export type BeneficiaryType = "company" | "individual";

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
  holderName: string;
  type: BeneficiaryType;
};
