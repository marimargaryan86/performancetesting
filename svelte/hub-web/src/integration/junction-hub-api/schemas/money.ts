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
