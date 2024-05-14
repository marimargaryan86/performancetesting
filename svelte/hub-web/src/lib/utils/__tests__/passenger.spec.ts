import { describe, expect, it } from "vitest";
import type { TripOfferPriceQuote } from "~/integration/junction-mobile-api/schemas";
import { getPassengerValidator } from "../passenger";

describe("passenger utils", () => {
  const mockRequiredFields: TripOfferPriceQuote["required"] = [
    "passport-number",
    "expiration-date",
    "issue-date",
    "issuing-country",
    "nationality",
    "residence-country-code",
  ];

  describe("getPassengerValidator", () => {
    it("returns a validator for the required fields", () => {
      const validator = getPassengerValidator(mockRequiredFields);
      const validPassenger = {
        firstName: "John",
        lastName: "Doe",
        title: "mr",
        gender: "male",
        birthDate: new Date("1990-01-01"),
        document: {
          type: "passport",
          number: "123456",
          expiryDate: new Date("2030-01-01"),
          issueDate: new Date("2020-01-01"),
          countryCodes: {
            issue: "US",
            nationality: "US",
            residence: "US",
          },
        },
      };
      const result = validator.safeParse(validPassenger);
      expect(result.success).toBe(true);
    });
  });
});
