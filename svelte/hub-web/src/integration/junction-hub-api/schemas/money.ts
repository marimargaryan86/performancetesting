export type Money = {
  currency: string;
  amount: number;
};

export type MoneySchema = {
  currency: string;
  amount: number;
};

export const moneyParser = {
  toModel: (data: MoneySchema): Money => ({
    currency: data.currency,
    amount: data.amount,
  }),
  toSchema: (data: Money): MoneySchema => ({
    currency: data.currency,
    amount: data.amount,
  }),
};

export type Price = {
  amount: number;
  currency: string;
};

export type PriceSchema = {
  amount: string;
  currency: string;
};

export const priceParser = {
  toModel: (data: PriceSchema): Price => ({
    amount: Number(data.amount),
    currency: data.currency,
  }),
  toSchema: (data: Price): PriceSchema => ({
    amount: data.amount.toString(),
    currency: data.currency,
  }),
};

export type PriceBreakdown = {
  price: Price;
  type: "base-fare" | "tax" | "reseller-mark-up" | "company-mark-up" | "service-mark-up";
};

export type PriceBreakdownSchema = {
  price: PriceSchema;
  breakdownType: "base-fare" | "tax" | "reseller-mark-up" | "company-mark-up" | "service-mark-up";
};

export const priceBreakdownParser = {
  toModel: (data: PriceBreakdownSchema): PriceBreakdown => ({
    price: priceParser.toModel(data.price),
    type: data.breakdownType,
  }),
};
