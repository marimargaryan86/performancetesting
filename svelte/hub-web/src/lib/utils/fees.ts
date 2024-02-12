import { roundCurrency } from "./money";

export const FEE_TYPES = ["flat-rate", "percentage"] as const;
export type FeeType = (typeof FEE_TYPES)[number];

/**
 * Given the markup fee type, raw input amount, and the baseline total price,
 * this returns the correct fee amount. Applies rounding to percentage-based
 * fees.
 *
 * @param {FeeType} type - Supported values are "flat-rate" or "percentage".
 * @param {number} inputAmount - The amount on which the fee is calculated.
 * @param {number} baselineAmount - When calculating a percentage, this is the baseline amount.
 * @returns {number} - The calculated fee rounded to the nearest hundredth. Returns `NaN` for unsupported fee types.
 *
 * @example
 * calcFeeAmount("flat-rate", 150.42, 0);        // returns 150.42
 * calcFeeAmount("percentage", 2, 1000);         // returns 20
 * calcFeeAmount("unsupported-type", 200, 1000); // returns NaN, should an incorrect type be passed
 */
export function calcFeeAmount(type: FeeType, inputAmount: number, baselineAmount: number): number {
  switch (type) {
    case "flat-rate":
      return roundCurrency(inputAmount);

    case "percentage":
      return roundCurrency((inputAmount / 100) * baselineAmount);

    default:
      return NaN;
  }
}
