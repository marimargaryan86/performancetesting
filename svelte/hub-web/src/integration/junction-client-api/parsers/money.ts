import type { MoneyModel } from "models/money";
import type { PriceSchema } from "../schemas/price";

export function parsePrice(price: PriceSchema): MoneyModel {
  return {
    amount: Number(price.amount),
    currency: price.currency,
  };
}
