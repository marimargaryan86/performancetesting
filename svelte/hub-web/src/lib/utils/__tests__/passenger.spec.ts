import { describe, expect, it } from "vitest";
import type { TripOfferPriceQuote } from "~/integration/junction-mobile-api/schemas";
import type { PassengerPickerData, PartialPassengerData } from "$lib/models/passenger";
import { getPassengerValidator, getDefaultPassengers } from "../passenger";

describe("passenger utils", () => {
  const mockRequiredFields: TripOfferPriceQuote["required"] = [
    "passport-number",
    "expiration-date",
    "issue-date",
    "issuing-country",
    "nationality",
    "residence-country-code",
  ];

  const mockPassengerPickerData: Partial<PassengerPickerData> = {
    adults: 2,
    youths15: 1,
    children6: 1,
  };

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

  describe("getDefaultPassengers", () => {
    it("returns an array of default passengers", () => {
      const result = getDefaultPassengers(mockPassengerPickerData as PassengerPickerData);
      const expected: PartialPassengerData[] = [
        { type: "adults" },
        { type: "adults" },
        { type: "youths15" },
        { type: "children6" },
      ];
      expect(result).toEqual(expected);
    });
  });
});
