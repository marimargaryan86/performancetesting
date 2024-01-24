import { describe, expect, it } from "vitest";
import { validatePassengerNameRecord } from "utils/booking";

describe("validatePassengerNameRecord", () => {
  it("should return `true` for valid reference numbers", () => {
    expect(validatePassengerNameRecord("abc12345")).toBe(true);
    expect(validatePassengerNameRecord("abcdEFGH")).toBe(true);
    expect(validatePassengerNameRecord("12345678")).toBe(true);
  });

  it("should return `false` for invalid reference numbers", () => {
    // not 8 characters
    expect(validatePassengerNameRecord("abc12")).toBe(false);
    // more than 8 characters
    expect(validatePassengerNameRecord("abcdefghi")).toBe(false);
    // includes non-alphanumeric character
    expect(validatePassengerNameRecord("abcd-123")).toBe(false);
  });
});
