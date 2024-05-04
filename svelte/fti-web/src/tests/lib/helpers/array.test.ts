import { describe, expect, it } from "vitest";
import { ensureDefined } from "$lib/helpers/array";

describe("ensureDefined", () => {
  it("should return true for non-undefined values", () => {
    expect(ensureDefined(0)).toBe(true);
    expect(ensureDefined("")).toBe(true);
    expect(ensureDefined(null)).toBe(true);
    expect(ensureDefined(false)).toBe(true);
    expect(ensureDefined([])).toBe(true);
    expect(ensureDefined({})).toBe(true);
  });

  it("should return false for undefined values", () => {
    expect(ensureDefined(undefined)).toBe(false);
  });
});
