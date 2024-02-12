import type { Partialize, Require } from "~/integration/ts-helpers";
import * as CommonSchemas from "~/integration/common/schemas";
import type { Currency, CurrencySchema } from "./currency";
import type { Account, AccountSchema } from "./account";
import type { IncludedMapping } from "./included";

export type BankDetailsBase = {
  name: string;
  bicSwift?: string;
  accountType: "checking" | "savings";
  paymentType: "priority" | "regular";
  address: Require<CommonSchemas.Address, "street" | "countryCode">;
};

export type BankDetailsAba = {
  type: "aba";
  accountNumber?: string;
  aba?: string;
};

export type BankDetailsIban = {
  type: "iban";
  iban?: string;
};

export type BankDetails = BankDetailsBase & (BankDetailsAba | BankDetailsIban);

export type BankDetailsBaseSchema = {
  name: string;
  bicSwift?: string | null;
  accountType: "checking" | "savings";
  paymentTypes: "priority" | "regular";
  address: Require<CommonSchemas.AddressSchema, "addressLines" | "countryCode">;
};

export type BankDetailsAbaSchema = {
  accountNumber: string | null;
  aba: string | null;
};

export type BankDetailsIbanSchema = {
  iban: string | null;
};

export type BankDetailsSchema = BankDetailsBaseSchema &
  (BankDetailsAbaSchema | BankDetailsIbanSchema);

export const bankDetailsParser = {
  toModel: (data: BankDetailsSchema): BankDetails => {
    const base: BankDetailsBase = {
      name: data.name,
      accountType: data.accountType,
      paymentType: data.paymentTypes,
      address: CommonSchemas.addressParser.toModel(data.address) as BankDetailsBase["address"],
      bicSwift: data.bicSwift ?? undefined,
    };

    if (!("iban" in data)) {
      return {
        ...base,
        type: "aba",
        accountNumber: data.accountNumber ?? undefined,
        aba: data.aba ?? undefined,
      };
    }

    return {
      ...base,
      type: "iban",
      iban: data.iban ?? undefined,
    };
  },
  toSchema: (data: BankDetails): BankDetailsSchema => {
    const base: BankDetailsBaseSchema = {
      name: data.name,
      accountType: data.accountType,
      paymentTypes: data.paymentType,
      address: CommonSchemas.addressParser.toSchema(
        data.address,
      ) as BankDetailsBaseSchema["address"],
      bicSwift: "bicSwift" in data ? data.bicSwift ?? null : undefined,
    };

    if (data.type === "aba") {
      return {
        ...base,
        accountNumber: data.accountNumber ?? null,
        aba: data.aba ?? null,
      };
    }

    return {
      ...base,
      iban: data.iban ?? null,
    };
  },
};

export type Beneficiary = {
  id: string;
  bankAccountHolderName: string;
  email: string;
  address: Require<CommonSchemas.EnhancedAddressDetails, "street" | "countryCode">;
  bankDetails: BankDetails;
  currencyId: string;
  currency?: Currency;
  accountId: string;
  account?: Account;
};

export type BeneficiaryPut = Partialize<Beneficiary, "id">;

export type BeneficiarySchema = {
  id: string;
  type: "beneficiaries";
  attributes: {
    bankAccountHolderName: string;
    email: string;
    beneficiaryAddress: Require<
      CommonSchemas.EnhancedAddressDetailsSchema,
      "addressLines" | "countryCode"
    >;
    bankDetails: BankDetailsSchema;
  };
  relationships: {
    currency: { data: Pick<CurrencySchema, "id" | "type"> };
    account: { data: Pick<AccountSchema, "id" | "type"> };
  };
};

export type BeneficiaryPutSchema = Pick<BeneficiarySchema, "type" | "relationships" | "attributes">;

export const beneficiaryParser = {
  toModel: (data: BeneficiarySchema, included?: IncludedMapping): Beneficiary => {
    const accountId = data.relationships.account.data.id;
    const currencyId = data.relationships.currency.data.id;

    return {
      id: data.id,
      bankAccountHolderName: data.attributes.bankAccountHolderName,
      address: CommonSchemas.enhancedAddressDetailsParser.toModel(
        data.attributes.beneficiaryAddress,
      ) as Beneficiary["address"],
      email: data.attributes.email,
      accountId,
      account: included?.accounts?.find(({ id }) => id === accountId),
      currencyId,
      currency: included?.currencies?.find(({ code }) => code === currencyId),
      bankDetails: bankDetailsParser.toModel(data.attributes.bankDetails),
    };
  },
  toPutSchema: (data: BeneficiaryPut): BeneficiaryPutSchema => ({
    type: "beneficiaries",
    attributes: {
      bankAccountHolderName: data.bankAccountHolderName,
      email: data.email,
      beneficiaryAddress: CommonSchemas.enhancedAddressDetailsParser.toSchema(
        data.address,
      ) as BeneficiaryPutSchema["attributes"]["beneficiaryAddress"],
      bankDetails: bankDetailsParser.toSchema(data.bankDetails),
    },
    relationships: {
      account: { data: { id: data.accountId, type: "accounts" } },
      currency: { data: { id: data.currencyId, type: "currencies" } },
    },
  }),
};
