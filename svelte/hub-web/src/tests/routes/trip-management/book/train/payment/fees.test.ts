import { describe, expect, it } from "vitest";
import {
  type FeeType,
  calcFeeAmount,
} from "$lib/components/pages/trip-management/booking-flow-train/payment/fees.svelte";

describe("calcFeeAmount", () => {
  it("calculates flat-rate fee correctly by rounding the input amount", () => {
    const fee = calcFeeAmount("flat-rate", 150.427, 0);
    expect(fee).toEqual(150.43);
  });

  it("calculates percentage-based fees correctly by applying percentage on baseline and rounding it", () => {
    const fee1 = calcFeeAmount("percentage", 10, 80);
    expect(fee1).toEqual(8);

    const fee2 = calcFeeAmount("percentage", 2.1235999, 1000);
    expect(fee2).toEqual(21.24);
  });

  it("returns NaN for unsupported fee types", () => {
    const fee = calcFeeAmount("unsupported-type" as FeeType, 200, 1000);
    expect(fee).toBeNaN();
  });

  it("handles zero values correctly", () => {
    const feeZeroInput = calcFeeAmount("flat-rate", 0, 500);
    expect(feeZeroInput).toEqual(0);

    const feeZeroBaseline = calcFeeAmount("percentage", 10, 0);
    expect(feeZeroBaseline).toEqual(0);
  });
});
