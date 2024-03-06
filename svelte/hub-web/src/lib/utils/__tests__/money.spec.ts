/* eslint-disable max-nested-callbacks */
import { describe, it, expect } from "vitest";
import { pricesEqual, summarizePrices, roundCurrency } from "../money";
import type { Price } from "~/integration/common/schemas";

describe("money utils", () => {
  describe("pricesEqual", () => {
    it("should return true when prices are equal", () => {
      const priceA: Price = { amount: 100, currency: "USD" };
      const priceB: Price = { amount: 100, currency: "USD" };
      expect(pricesEqual(priceA, priceB)).toBe(true);
    });

    it("should return false when prices are not equal", () => {
      const priceA: Price = { amount: 100, currency: "USD" };
      const priceB: Price = { amount: 200, currency: "USD" };
      expect(pricesEqual(priceA, priceB)).toBe(false);
    });
  });

  describe("summarizePrices", () => {
    it("should summarize prices correctly", () => {
      const prices: Price[] = [
        { amount: 100, currency: "USD" },
        { amount: 200, currency: "USD" },
        { amount: 300, currency: "USD" },
      ];
      const summary = summarizePrices(...prices);
      expect(summary).toEqual({ amount: 600, currency: "USD" });
    });

    it("should throw an error when currencies do not match", () => {
      const prices: Price[] = [
        { amount: 100, currency: "USD" },
        { amount: 200, currency: "EUR" },
      ];
      expect(() => summarizePrices(...prices)).toThrow("Currencies do not match");
    });

    it("should summarize a single price correctly", () => {
      const price: Price = { amount: 100, currency: "USD" };
      const summary = summarizePrices(price);
      expect(summary).toEqual(price);
    });

    it("should throw an error when currencies don't match", () => {
      const prices: Price[] = [
        { amount: 100, currency: "USD" },
        { amount: 200, currency: "EUR" },
      ];
      expect(() => summarizePrices(...prices)).toThrow("Currencies do not match");
    });

    it("should throw an error when no prices are provided", () => {
      expect(() => summarizePrices()).toThrow("No prices provided");
    });
  });

  describe("roundCurrency", () => {
    it("should round currency correctly with positive numbers", () => {
      expect(roundCurrency(1.005)).toBe(1.01);
      expect(roundCurrency(10.018)).toBe(10.02);
    });

    it("should round currency correctly with negative numbers", () => {
      expect(roundCurrency(-1.005)).toBe(-1.01);
      expect(roundCurrency(-10.018)).toBe(-10.02);
    });
  });
});
