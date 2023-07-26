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
    city: address.city as string,
    postalCode: address.postalCode as string,
    state: address.state ?? undefined,
  };
}

export function parseBankDetailsSchema(bankDetails: BankDetailsSchema): BankDetailsModel {
  const base: BankDetailsBaseModel = {
    accountType: bankDetails.accountType,
    address: bankDetails.address,
    name: bankDetails.name,
    paymentType: bankDetails.paymentTypes,
    bicSwift: bankDetails.bicSwift as string,
  };

  if ("accountNumber" in bankDetails) {
    return {
      ...base,
      type: "aba",
      accountNumber: bankDetails.accountNumber as string,
      aba: bankDetails.aba as string,
    };
  }

  return {
    ...base,
    type: "iban",
    iban: bankDetails.iban as string,
  };
}

export function parseBeneficiarySchema(beneficiary: BeneficiarySchema): BeneficiaryModel {
  const { attributes, relationships } = beneficiary;

  return {
    id: beneficiary.id,
    companyName: attributes.bankAccountHolderName,
    email: attributes.email,
    address: parseEnhancesAddressDetailsSchema(attributes.beneficiaryAddress),
    bankDetails: parseBankDetailsSchema(attributes.bankDetails),
    accountId: relationships.account.data.id,
    currencyCode: relationships.currency.data.id,
  };
}

// eslint-disable-next-line max-lines-per-function
export function parseBeneficiaryModel(
  beneficiary: Omit<BeneficiaryModel, "id"> & { id?: string },
): Omit<BeneficiarySchema, "links" | "id"> {
  const { bankDetails, address } = beneficiary;

  return {
    type: "beneficiaries",
    attributes: {
      bankAccountHolderName: beneficiary.companyName,
      bankDetails: {
        bicSwift: bankDetails.bicSwift,
        accountType: bankDetails.accountType,
        name: bankDetails.name,
        address: {
          addressLines: bankDetails.address.addressLines,
          countryCode: bankDetails.address.countryCode,
        },
        paymentTypes: bankDetails.paymentType,
        ...(bankDetails.type === "aba"
          ? {
              aba: bankDetails.aba,
              accountNumber: bankDetails.accountNumber,
            }
          : {
              iban: bankDetails.iban,
            }),
      },
      beneficiaryAddress: {
        addressLines: address.addressLines,
        countryCode: address.countryCode,
        city: address.city,
        postalCode: address.postalCode,
        state: address.state,
      },
      email: beneficiary.email,
    },
    relationships: {
      account: {
        data: {
          type: "accounts",
          id: beneficiary.accountId,
        },
      },
      currency: {
        data: {
          type: "currencies",
          id: beneficiary.currencyCode,
        },
      },
    },
  };
}
