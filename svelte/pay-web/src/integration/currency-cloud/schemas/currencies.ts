export type CurrencySchema = {
  code: string;
  decimal_places: number;
  name: string;
  online_trading: boolean;
  can_buy: boolean;
  can_sell: boolean;
};

export type FindCurrenciesResponseSchema = {
  currencies: CurrencySchema[];
};
