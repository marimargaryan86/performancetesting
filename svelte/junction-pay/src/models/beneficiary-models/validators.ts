import utils from "$src/lib/utils";
import type {
  AccountDetailsData,
  AccountDetailsError,
  BankAccountDetailsData,
  BankAccountDetailsError,
  BeneficiaryData,
  BeneficiaryDetailsData,
  BeneficiaryDetailsError,
  BeneficiaryError,
  CompanyDetailsData,
  CompanyDetailsError,
  EntityDetailsData,
  EntityDetailsError,
  IndividualDetailsData,
  IndividualDetailsError,
  PaymentOptionsData,
  PaymentOptionsError,
  PaymentTypeData,
  PaymentTypeError,
} from "./models";

export function validateBeneficiaryDetails(
  data: Partial<BeneficiaryDetailsData>,
): BeneficiaryDetailsError | undefined {
  return utils.formatErrors({
    nickname: !data.nickname?.trim().length ? ["Nickname is missing"] : undefined,
    accountCountry: !data.accountCountry ? ["Account country is missing"] : undefined,
    accountCurrency: !data.accountCurrency ? ["Account currency is missing"] : undefined,
    addressCountry: !data.addressCountry ? ["Beneficiary country is missing"] : undefined,
  });
}

export function validatePaymentTypeDetails(
  data: Partial<PaymentTypeData>,
): PaymentTypeError | undefined {
  return utils.formatErrors({
    paymentTypes: !data.paymentTypes?.length ? ["Payment type is missing"] : undefined,
    addressCountry: !data.addressCountry ? ["Beneficiary country is missing"] : undefined,
    addressLine: !data.addressLine?.trim().length ? ["Beneficiary address is missing"] : undefined,
    addressPostalCode: !data.addressPostalCode?.trim().length
      ? ["Beneficiary postal code is missing"]
      : undefined,
  });
}

export function validatePaymentOptions(
  data: Partial<PaymentOptionsData>,
): PaymentOptionsError | undefined {
  return utils.formatErrors({
    paymentOptions: !data.paymentOptions?.length ? ["Missing payment option"] : undefined,
    sortCode:
      data.paymentOptions?.includes("sort-code") && !data.sortCode?.trim().length
        ? ["Missing sort code"]
        : undefined,
    bicSwift:
      data.paymentOptions?.includes("swift") && !data.bicSwift?.trim().length
        ? ["Missing BIC/SWIFT"]
        : undefined,
    iban:
      data.paymentOptions?.includes("swift") && !data.iban?.trim().length
        ? ["Missing IBAN"]
        : undefined,
  });
}

export function validateCompanyDetails(
  data: Partial<CompanyDetailsData>,
): CompanyDetailsError | undefined {
  return utils.formatErrors({
    companyName: !data.companyName?.trim().length ? ["Company name is missing"] : undefined,
    companyRegistrationDate: !data.companyRegistrationDate
      ? ["Registration date is missing"]
      : undefined,
  });
}

export function validateIndividualDetails(
  data: Partial<IndividualDetailsData>,
): IndividualDetailsError | undefined {
  return utils.formatErrors({
    individualBirthDate: !data.individualBirthDate ? ["Birth date is missing"] : undefined,
    individualFirstName: !data.individualFirstName?.trim().length
      ? ["First name is missing"]
      : undefined,
    individualLastName: !data.individualLastName?.trim().length
      ? ["Last name is missing"]
      : undefined,
  });
}

export function validateEntityDetails(
  data: Partial<EntityDetailsData>,
): EntityDetailsError | undefined {
  if (data.type === "company") {
    return validateCompanyDetails(data);
  } else if (data.type === "individual") {
    return validateIndividualDetails(data);
  }
}

export function validateAccountDetails(
  data: Partial<AccountDetailsData>,
): AccountDetailsError | undefined {
  return utils.formatErrors({
    accountCountry: !data.accountCountry ? ["Account country missing"] : undefined,
    accountCity: !data.accountCity?.trim().length ? ["Account city missing"] : undefined,
    accountCurrency: !data.accountCurrency ? ["Account currency missing"] : undefined,
    accountHolderName: !data.accountHolderName?.trim().length
      ? ["Account holder name missing"]
      : undefined,
    accountNumber: !data.accountNumber?.trim().length ? ["Account number missing"] : undefined,
  });
}

export function validateBankAccountDetails(
  data: Partial<BankAccountDetailsData>,
): BankAccountDetailsError | undefined {
  return utils.formatErrors({
    ...validateEntityDetails(data),
    ...validateAccountDetails(data),
    ...validatePaymentTypeDetails(data),
    ...validatePaymentOptions(data),
  });
}

export function validateBeneficiaryData(
  data: Partial<BeneficiaryData>,
): BeneficiaryError | undefined {
  return utils.formatErrors({
    ...validateBeneficiaryDetails(data),
    ...validateBankAccountDetails(data),
  });
}
