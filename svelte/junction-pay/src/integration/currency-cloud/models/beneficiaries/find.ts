import type { BankAccountType, EntityType, ScopeType } from "../../schemas/beneficiaries";
import type { OrderDirection } from "../../schemas/common";
import type { OrderField as OrderFieldCC } from "../../schemas/beneficiaries";

export const orderFields = [
  "bankAccountNumber",
  "bankAccountHolderName",
  "bankAccountType",
  "bankAccountCountryCode",
  "bankAccountBic",
  "bankAccountCurrency",
  "defaultBeneficiary",
  "bankAccountIban",
  "nickname",
] as const;

export type OrderField = typeof orderFields[number];

export const orderFieldMapping: Record<OrderField, OrderFieldCC> = {
  bankAccountNumber: "account_number",
  bankAccountHolderName: "bank_account_holder_name",
  bankAccountType: "bank_account_type",
  bankAccountCountryCode: "beneficiary_country",
  bankAccountBic: "bic_swift",
  bankAccountCurrency: "currency",
  defaultBeneficiary: "default_beneficiary",
  bankAccountIban: "iban",
  nickname: "name",
};

export type FindCriteriaBaseModel<T = EntityType | undefined> = {
  onBehalfOf?: string;
  nickname?: string;
  defaultBeneficiary?: boolean;
  entityType?: T;
  bank?: {
    account?: {
      holderName?: string;
      currencyCode?: string;
      number?: string;
      sortCode?: string;
      bic?: string;
      iban?: string;
      type?: BankAccountType;
    };
    name?: string;
  };
  contact?: {
    postalCode?: string;
    city?: string;
    stateOrProvince?: string;
    countryCode?: string;
    externalReference?: string;
  };
  scope?: ScopeType;
  limit?: number;
  offset?: number;
  order?: OrderField;
  orderDirection?: OrderDirection;
};

export type FindCriteriaModel<T = EntityType | undefined> = T extends "company"
  ? FindCriteriaBaseModel<T> & {
      company?: {
        name?: string;
        registrationDate?: Date;
      };
    }
  : T extends "individual"
  ? FindCriteriaBaseModel<T> & {
      individual?: {
        firstName?: string;
        lastName?: string;
        birthDate?: Date;
      };
    }
  : never;
