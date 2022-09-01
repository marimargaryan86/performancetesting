import type { EntityType, IdentificationType } from "./beneficiaries";
import type { OrderDirection } from "./common";

export const accountStatuses = ["enabled", "enabled_no_trading", "disabled"] as const;

export type AccountStatus = typeof accountStatuses[number];

export const settlementTypes = ["net"] as const;

export type SettlementType = typeof settlementTypes[number];

export const accountVerificationStatuses = ["yes", "no", "not required"] as const;

export type AccountVerificationStatus = typeof accountVerificationStatuses[number];

export type AccountSchema = {
  id: string;
  account_name: string;
  brand: string;
  your_reference: string | null;
  status: AccountStatus;
  street: string;
  city: string;
  state_or_province: string | null;
  country: string;
  postal_code: string;
  spread_table: string;
  legal_entity_type: EntityType;
  created_at: string;
  updated_at: string;
  identification_type: IdentificationType | null;
  identification_value: string | null;
  short_reference: string;
  api_trading: boolean;
  online_trading: boolean;
  phone_trading: boolean;
  process_third_party_funds: boolean;
  settlement_type: SettlementType;
  agent_or_reliance: boolean;
  terms_and_conditions_accepted: boolean | null;
  bank_account_verified: AccountVerificationStatus;
};

export type FindAccountsResponseSchema = {
  accounts: AccountSchema[];
  pagination: {
    total_entries: number;
    total_pages: number;
    current_page: number;
    per_page: number;
    previous_page: number;
    next_page: number;
    order: string;
    order_asc_desc: OrderDirection;
  };
};

export const orderFields = [
  "account_name",
  "brand",
  "your_reference",
  "status",
  "street",
  "city",
  "state_or_province",
  "postal_code",
  "country",
  "spread_table",
  "bank_account_verified",
] as const;

export type OrderField = typeof orderFields[number];

export type FindCriteriaSchema = {
  account_name?: string;
  brand?: string;
  your_reference?: string;
  status?: AccountStatus;
  street?: string;
  city?: string;
  state_or_province?: string;
  postal_code?: string;
  country?: string;
  spread_table?: string;
  page?: number;
  per_page?: number;
  order?: OrderField;
  order_asc_desc?: OrderDirection;
  bank_account_verified?: AccountVerificationStatus;
};
