import type * as MobileSchemas from "~/integration/junction-mobile-api/schemas";
import { z } from "zod";
import type { PartialPassengerData, PassengerPickerData } from "$lib/models/passenger";

const countryCodesValidator = z.object({
  issue: z
    .string({ required_error: "Issuing country is required" })
    .regex(/^[A-z]{2}$/)
    .optional(),
  nationality: z
    .string({ required_error: "Nationality country is required" })
    .regex(/^[A-z]{2}$/)
    .optional(),
  residence: z
    .string({ required_error: "Residence country is required" })
    .regex(/^[A-z]{2}$/)
    .optional(),
});
type CountryCodesValidator = z.infer<typeof countryCodesValidator>;

const documentValidator = z.object({
  type: z.literal("passport").optional(),
  number: z.string({ required_error: "Document number is required" }).trim().min(1).optional(),
  expiryDate: z.date({ required_error: "Expiry date is required" }).optional(),
  issueDate: z.date({ required_error: "Issuing date is required" }).optional(),
  countryCodes: countryCodesValidator.optional(),
});
type DocumentValidator = z.infer<typeof documentValidator>;

const passengerValidator = z.object({
  firstName: z
    .string({ required_error: "First name is required" })
    .trim()
    .min(1, "First name must be at least one character"),
  lastName: z
    .string({ required_error: "Last name is required" })
    .trim()
    .min(1, "Last name must be at least one character"),
  title: z.enum(["unspecified", "mr", "mrs", "ms", "miss"], {
    required_error: "Title is required",
  }),
  gender: z.enum(["unspecified", "male", "female"], { required_error: "Gender is required" }),
  birthDate: z.date({ required_error: "Birth date is required" }),
  document: documentValidator.optional(),
});
export type PassengerValidator = z.infer<typeof passengerValidator>;

export function getPassengerValidator(
  requiredFields: MobileSchemas.TripOfferPriceQuote["required"],
): typeof passengerValidator {
  const nextPassengerValidator: Partial<Record<keyof PassengerValidator, z.ZodTypeAny>> = {};
  const nextDocumentValidator: Partial<Record<keyof DocumentValidator, z.ZodTypeAny>> = {};
  const nextCountryCodesValidator: Partial<Record<keyof CountryCodesValidator, z.ZodTypeAny>> = {};

  requiredFields.forEach((field) => {
    if (field === "passport-number") {
      nextDocumentValidator.number = documentValidator.shape.number.unwrap();
    } else if (field === "expiration-date") {
      nextDocumentValidator.expiryDate = documentValidator.shape.expiryDate.unwrap();
    } else if (field === "issue-date") {
      nextDocumentValidator.issueDate = documentValidator.shape.issueDate.unwrap();
    } else if (field === "issuing-country") {
      nextCountryCodesValidator.issue = countryCodesValidator.shape.issue.unwrap();
    } else if (field === "nationality") {
      nextCountryCodesValidator.nationality = countryCodesValidator.shape.nationality.unwrap();
    } else if (field === "residence-country-code") {
      nextCountryCodesValidator.residence = countryCodesValidator.shape.residence.unwrap();
    }
  });

  if (Object.keys(nextCountryCodesValidator).length) {
    nextDocumentValidator.countryCodes = countryCodesValidator.extend({
      ...nextCountryCodesValidator,
    });
  }

  if (Object.keys(nextDocumentValidator).length) {
    nextPassengerValidator.document = documentValidator.extend({ ...nextDocumentValidator });
  }

  if (Object.keys(nextPassengerValidator).length) {
    return passengerValidator.extend({ ...nextPassengerValidator }) as typeof passengerValidator;
  }

  return passengerValidator;
}

export function getDefaultPassengers(passengers: PassengerPickerData): PartialPassengerData[] {
  return (Object.keys(passengers) as unknown as (keyof PassengerPickerData)[]).flatMap((type) =>
    Array(passengers[type])
      .fill(undefined)
      .map<PartialPassengerData>(() => ({ type })),
  );
}
