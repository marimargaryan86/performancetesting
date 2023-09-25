import type { PriceModel } from "integration/junction-mobile-api/schemas/price";

export function summarizePrices(...prices: [PriceModel, ...PriceModel[]]): PriceModel {
  if (new Set(prices.flatMap((price) => price.currency)).size !== 1) {
    throw new Error("Currencies do not match");
  }

  return {
    currency: prices[0].currency,
    amount: prices.reduce((prev, curr) => prev + curr.amount, 0),
  };
}
