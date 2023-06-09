import type {
  BankDetailsBaseModel,
  BankDetailsModel,
  BeneficiaryModel,
  EnhancedAddressDetailsModel,
} from "models/beneficiary";
import type {
  BankDetailsSchema,
  BeneficiarySchema,
  EnhancedAddressDetails,
} from "../schemas/beneficiaty";

export function parseEnhancesAddressDetailsSchema(
  address: EnhancedAddressDetails,
): EnhancedAddressDetailsModel {
  return {
    addressLines: address.addressLines,
    countryCode: address.countryCode,
    city: address.city,
    postalCode: address.postalCode,
    state: address.state ?? undefined,
  };
}

export function parseBankDetailsSchema(bankDetails: BankDetailsSchema): BankDetailsModel {
  const base: BankDetailsBaseModel = {
    accountType: bankDetails.accountType,
    address: bankDetails.address,
    name: bankDetails.name,
    paymentTypes: bankDetails.paymentTypes,
    bicSwift: bankDetails.bicSwift ?? undefined,
  };

  if ("accountNumber" in bankDetails) {
    return {
      ...base,
      type: "aba",
      accountNumber: bankDetails.accountNumber ?? undefined,
      aba: bankDetails.aba ?? undefined,
    };
  }

  return {
    ...base,
    type: "iban",
    iban: bankDetails.iban ?? undefined,
  };
}

export function parseBeneficiarySchema(beneficiary: BeneficiarySchema): BeneficiaryModel {
  const { attributes, relationships } = beneficiary;

  return {
    id: beneficiary.id,
    bankAccountHolderName: attributes.bankAccountHolderName,
    email: attributes.email,
    address: parseEnhancesAddressDetailsSchema(attributes.beneficiaryAddress),
    bankDetails: parseBankDetailsSchema(attributes.bankDetails),
    accountId: relationships.account.data.id,
    currencyCode: relationships.currency.data.id,
  };
}
