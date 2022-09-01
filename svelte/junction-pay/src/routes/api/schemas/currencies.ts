import type { OrderField, TradeType } from "$integration/currency-cloud/models/currencies";

export type FindCriteriaSchema = {
  "page[limit]"?: number;
  "page[offset]"?: number;
  "orderBy[asc]"?: OrderField;
  "orderBy[desc]"?: OrderField;
};

export type CurrencySchema = {
  code: string;
  decimals: number;
  name: string;
  tradable: boolean;
  tradeTypes: TradeType[];
};

export type FindCurrenciesResponse = CurrencySchema[];
