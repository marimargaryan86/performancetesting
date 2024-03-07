import { describe, it, expect } from "vitest";
import { calcFeeAmount, type FeeType } from "../fees";

describe("calcFeeAmount", () => {
  it("should calculate flat-rate fees correctly", () => {
    const fee = calcFeeAmount("flat-rate" as FeeType, 150.42, 0);
    expect(fee).toBe(150.42);
  });

  it("should calculate percentage fees correctly", () => {
    const fee = calcFeeAmount("percentage" as FeeType, 2, 1000);
    expect(fee).toBe(20);
  });

  it("should return NaN for unsupported fee types", () => {
    const fee = calcFeeAmount("unsupported-type" as FeeType, 200, 1000);
    expect(fee).toBeNaN();
  });
});
