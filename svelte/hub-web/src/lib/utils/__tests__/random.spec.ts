import { describe, expect, it } from "vitest";
import { getRandomId, getRandomAlphaNumericString } from "../random";

describe("random utils", () => {
  describe("getRandomId", () => {
    it("returns a random ID with the given prefix", () => {
      const id = getRandomId("test");
      expect(id.startsWith("test-")).toBe(true);
    });

    it("returns a random ID with the default prefix if no prefix is given", () => {
      const id = getRandomId();
      expect(id.startsWith("a-")).toBe(true);
    });
  });

  describe("getRandomAlphaNumericString", () => {
    it("returns a random alphanumeric string of the given length", () => {
      const str = getRandomAlphaNumericString(10);
      expect(str.length).toBe(10);
      expect(/^[a-zA-Z0-9]+$/.test(str)).toBe(true);
    });
  });
});
