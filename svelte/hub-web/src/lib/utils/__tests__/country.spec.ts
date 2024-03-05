import { describe, it, expect } from "vitest";
import { findCountry, getPhoneNumber } from "../country";
import type { CountryModel } from "$lib/models/location";

describe("findCountry", () => {
  it("should return true when query matches country code", () => {
    const country: CountryModel = {
      code: "US",
      name: "United States",
      phoneCode: "+1",
    };
    expect(findCountry("us", country)).toBe(true);
  });

  it("should return false when query does not match any country properties", () => {
    const country: CountryModel = {
      code: "US",
      name: "United States",
      phoneCode: "+1",
    };
    expect(findCountry("xyz", country)).toBe(false);
  });
});

describe("getPhoneNumber", () => {
  // TODO(2024-03-05): Test fails because our logic and data is too simplistic as Canada and US both have +1
  // Suggested solution is to replace it with libphonenumbers
  it.skip("should return the country and number when number has a US country code", () => {
    const country: CountryModel = {
      code: "US",
      name: "United States",
      phoneCode: "1",
    };
    const result = getPhoneNumber("+1123123123");
    expect(result.country).toEqual(country);
    expect(result.number).toBe("123123123");
  });

  it("should return the country and number when number has a United Kingdom country code", () => {
    const country: CountryModel = {
      code: "GB",
      name: "United Kingdom",
      phoneCode: "44",
    };
    const result = getPhoneNumber("+44123123123");
    expect(result.country).toEqual(country);
    expect(result.number).toBe("123123123");
  });

  it("should return the country and number when number has a Spanish country code", () => {
    const country: CountryModel = {
      code: "ES",
      name: "Spain",
      phoneCode: "34",
    };
    const result = getPhoneNumber("+34123123123");
    expect(result.country).toEqual(country);
    expect(result.number).toBe("123123123");
  });
});
