import { describe, it, expect } from "vitest";
import { getCookieName, SECURE_PREFIX } from "../helpers";

describe("getCookieName", () => {
  it("Should get a cookie name", () => {
    expect(getCookieName("foo", {})).toBe("foo");
    expect(getCookieName("foo", { secure: true })).toBe(`${SECURE_PREFIX}foo`);
  });
});
