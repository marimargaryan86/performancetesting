import type { Price } from "integration/common/schemas/price";

export function summarizePrices(...prices: [Price, ...Price[]]): Price {
  if (new Set(prices.flatMap((price) => price.currency)).size !== 1) {
    throw new Error("Currencies do not match");
  }

  return {
    currency: prices[0].currency,
    amount: prices.reduce((prev, curr) => prev + curr.amount, 0),
  };
}

/**
 * Rounds a number to the nearest hundredth. Intended for currency formatting.
 *
 * Fixes floating-point precision issues by adding a small epsilon before
 * rounding up. Rounding is more predictable in cases like 1.005 => 1.01.
 *
 * @param {number} num - The number representing currency to be rounded
 * @returns {number} - The input number rounded to the nearest hundredth (2 decimal places)
 *
 * @example
 * roundCurrency(1.005);  // returns 1.01
 * roundCurrency(-1.005); // returns -1.01
 * roundCurrency(10.018); // returns 10.02
 */
export function roundCurrency(num: number): number {
  const SIGNED_EPSILON = num < 0 ? -Number.EPSILON : Number.EPSILON;

  return Math.round((num + SIGNED_EPSILON) * 100) / 100;
}
