import type { MoneyModel } from "models/money";
import type { PriceBreakdownSchema, PriceSchema } from "../schemas/price";
import type { PriceBreakdownModel } from "models/booking/money";

export function parsePriceSchema(data: PriceSchema): MoneyModel {
  return {
    amount: Number(data.amount),
    currency: data.currency,
  };
}

export function parsePriceBreakdownSchema(data: PriceBreakdownSchema): PriceBreakdownModel {
  return {
    price: parsePriceSchema(data.price),
    type: data.breakdownType,
  };
}
