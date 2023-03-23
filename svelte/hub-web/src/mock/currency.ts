import type { MoneyModel } from "models/money";

const mockBalances: MoneyModel[] = [
  {
    currency: "EUR",
    amount: 12875.24,
  },
  {
    currency: "GBP",
    amount: 11832.12,
  },
  {
    currency: "USD",
    amount: 9857.29,
  },
];

export { mockBalances };
