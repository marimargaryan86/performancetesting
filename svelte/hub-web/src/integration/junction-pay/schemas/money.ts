export interface MoneySchema {
  currency: string;
  amount: number;
}

export interface CurrencyIdentifierSchema {
  id: string;
  type: "currencies";
}

export interface CurrencySchema extends CurrencyIdentifierSchema {
  attributes: {
    name: string;
    minorUnits: number;
  };
  links: { self: string };
}

export interface ListCurrenciesResponseSchema {
  data: CurrencySchema[];
  links: { next: string };
}
