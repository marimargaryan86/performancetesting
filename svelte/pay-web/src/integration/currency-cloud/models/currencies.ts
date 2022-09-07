import type { OrderDirection } from "../schemas/common";

export const tradeTypes = ["buy", "sell"] as const;

export type TradeType = typeof tradeTypes[number];

export type CurrencyModel = {
  code: string;
  decimals: number;
  name: string;
  tradable: boolean;
  tradeTypes: TradeType[];
};

export const orderFields = ["code", "name"] as const;

export type OrderField = typeof orderFields[number];

export type FindCriteriaModel = {
  limit?: number;
  offset?: number;
  order?: OrderField;
  orderDirection?: OrderDirection;
};
