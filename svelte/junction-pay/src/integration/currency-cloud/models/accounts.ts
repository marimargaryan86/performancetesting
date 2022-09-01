import type { AccountStatus, AccountVerificationStatus, SettlementType } from "../schemas/accounts";
import type { EntityType, IdentificationType } from "../schemas/beneficiaries";
import type { OrderDirection } from "../schemas/common";

export type AccountModel = {
  id: string;
  name: string;
  brand: string;
  ref: string | null;
  status: AccountStatus;
  contact: {
    address: string;
    postalCode: string;
    city: string;
    stateOrProvince: string | null;
    countryCode: string;
  };
  spreadTable: string;
  entityType: EntityType;
  createdAt: Date;
  modifiedAt: Date;
  identification: {
    type: IdentificationType;
    value: string;
  } | null;
  shortRef: string;
  apiTrading: boolean;
  onlineTrading: boolean;
  phoneTrading: boolean;
  processThirdPartyFunds: boolean;
  settlementType: SettlementType;
  agentOrReliance: boolean;
  termsAndConditionsAccepted: boolean | null;
  bankAccountVerificationStatus: AccountVerificationStatus;
};

export const orderFieldMapping = {
  name: "account_name",
  brand: "brand",
  ref: "your_reference",
  status: "status",
  contactAddress: "street",
  contactCity: "city",
  contactStateOrProvince: "state_or_province",
  contactPostalCode: "postal_code",
  contactCountryCode: "country",
  spreadTable: "spread_table",
  bankAccountVerificationStatus: "bank_account_verified",
} as const;

export const orderFields = Object.keys(orderFieldMapping).map(
  (item) => item,
) as (keyof typeof orderFieldMapping)[];

export type OrderField = typeof orderFields[number];

export type FindCriteriaModel = {
  name?: string;
  brand?: string;
  ref?: string;
  status?: AccountStatus;
  contact?: {
    address?: string;
    postalCode?: string;
    city?: string;
    stateOrProvince?: string;
    countryCode?: string;
  };
  spreadTable?: string;
  bankAccountVerificationStatus?: AccountVerificationStatus;
  offset?: number;
  limit?: number;
  order?: OrderField;
  orderDirection?: OrderDirection;
};
