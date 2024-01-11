import { describe, expect, it } from "vitest";
import { validateReferenceNumber } from "utils/booking";

describe("validateReferenceNumber", () => {
  it("should return `true` for valid reference numbers", () => {
    expect(validateReferenceNumber("abc12345")).toBe(true);
    expect(validateReferenceNumber("abcdEFGH")).toBe(true);
    expect(validateReferenceNumber("12345678")).toBe(true);
  });

  it("should return `false` for invalid reference numbers", () => {
    // not 8 characters
    expect(validateReferenceNumber("abc12")).toBe(false);
    // more than 8 characters
    expect(validateReferenceNumber("abcdefghi")).toBe(false);
    // includes non-alphanumeric character
    expect(validateReferenceNumber("abcd-123")).toBe(false);
  });
});
