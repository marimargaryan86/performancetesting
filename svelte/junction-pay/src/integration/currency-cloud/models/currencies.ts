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

export const orderFieldMapping = {
  code: "code",
  name: "name",
};

export const orderFields = Object.keys(orderFieldMapping).map(
  (item) => item,
) as (keyof typeof orderFieldMapping)[];

export type OrderField = typeof orderFields[number];

export type FindCriteriaModel = {
  limit?: number;
  offset?: number;
  order?: OrderField;
  orderDirection?: OrderDirection;
};
