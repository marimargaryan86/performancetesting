import { describe, expect, it, test } from "vitest";
import { match, getSearchTypeFromURL } from "../../../params/search_type";

describe("match function", () => {
  test.each([
    ["hotels", true],
    ["packages", true],
    ["car-rentals", true],
    ["cruises", false],
    ["flights", false],
    ["", false],
  ])("match(%s) should return %s", (input, expected) => {
    expect(match(input)).toBe(expected);
  });
});

describe("getSearchTypeFromURL function", () => {
  it("should extract the search type correctly from a well-formed URL", () => {
    const url = new URL("http://junction.bigxtra.dev/search/packages/origin/destination/");
    expect(getSearchTypeFromURL(url)).toBe("packages");
  });

  it("should throw an error if the URL path is too short", () => {
    const url = new URL("http://junction.bigxtra.dev/search/");
    expect(() => getSearchTypeFromURL(url)).toThrow(
      "Invalid URL format for extracting search type.",
    );
  });

  it("should throw an error if the search type is invalid", () => {
    const url = new URL("http://junction.bigxtra.dev/search/cars/origin/destination/");
    expect(() => getSearchTypeFromURL(url)).toThrow("Invalid search type.");
  });
});
