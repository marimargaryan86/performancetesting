import { describe, it, expect } from "vitest";
import { ensureDefined, isReference } from "../helpers";

describe("ensureDefined", () => {
  it("Should ensure that an object is defined", () => {
    expect(ensureDefined(null)).toBe(true);
    expect(ensureDefined("null")).toBe(true);
    expect(ensureDefined([])).toBe(true);
    expect(ensureDefined({})).toBe(true);
    expect(ensureDefined(undefined)).toBe(false);
  });
});

describe("isReference", () => {
  it("Should ensure that a schema is a reference", () => {
    expect(isReference({})).toBe(false);
    expect(isReference(null)).toBe(false);
    expect(isReference("foo")).toBe(false);
    expect(isReference({ foo: "bar" })).toBe(false);
    expect(isReference({ $ref: "foo" })).toBe(true);
    expect(isReference({ $ref: "foo", bar: "baz" })).toBe(true);
  });
});
