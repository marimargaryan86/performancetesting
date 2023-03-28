export interface MoneyModel {
  amount: number;
  currency: string;
}

export interface CurrencyModel {
  name: string;
  code: string;
  minorUnits: number;
}
