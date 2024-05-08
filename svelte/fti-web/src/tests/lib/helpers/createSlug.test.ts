import { describe, expect, it } from "vitest";
import { createSlug } from "$lib/helpers/common";

describe("createSlug", () => {
  it("should convert spaces to hyphens and lowercase all characters", () => {
    const name = "The Grand Hotel";
    const slug = createSlug(name);
    expect(slug).toBe("the-grand-hotel");
  });

  it("should remove any non-alphanumeric characters except hyphens", () => {
    const name = "Marriott's Resort & Spa";
    const slug = createSlug(name);
    expect(slug).toBe("marriotts-resort-spa");
  });

  it("should handle hotel names with multiple special characters correctly", () => {
    const name = "Holiday Inn Express Suites";
    const slug = createSlug(name);
    expect(slug).toBe("holiday-inn-express-suites");
  });

  it("should return an empty string when provided with an empty input", () => {
    const name = "";
    const slug = createSlug(name);
    expect(slug).toBe("");
  });

  it("should handle hotel names composed entirely of special characters", () => {
    const name = "####!!!$$$";
    const slug = createSlug(name);
    expect(slug).toBe("");
  });

  it("should manage hotel names with no spaces or special characters", () => {
    const name = "Fairmont";
    const slug = createSlug(name);
    expect(slug).toBe("fairmont");
  });
});
