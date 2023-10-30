import { describe, expect, it } from "vitest";
import { roundCurrency } from "utils/money";

describe("roundCurrency", () => {
  it("rounds 1.005 to 1.01 (addressing floating point precision issue)", () => {
    expect(roundCurrency(1.005)).toEqual(1.01);
  });

  it("rounds 10.018 to 10.02", () => {
    expect(roundCurrency(10.018)).toEqual(10.02);
  });

  it("does not modify already rounded numbers, e.g., 10.02 remains 10.02", () => {
    expect(roundCurrency(10.02)).toEqual(10.02);
  });

  it("rounds 1.234 to 1.23", () => {
    expect(roundCurrency(1.234)).toEqual(1.23);
  });

  it("handles zero correctly", () => {
    expect(roundCurrency(0)).toEqual(0);
  });

  it("handles negative numbers, e.g., rounds -1.005 to -1.01", () => {
    expect(roundCurrency(-1.005)).toEqual(-1.01);
  });
});
