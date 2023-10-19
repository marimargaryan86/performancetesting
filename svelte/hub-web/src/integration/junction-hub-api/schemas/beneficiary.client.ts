import { z } from "zod";

export const addressDetails = z.object({
  addressLines: z.array(z.string().max(255).trim()).min(1),
  countryCode: z.string().regex(/^[A-Z]{2}$/),
});

export const enhancedAddressDetails = addressDetails.extend({
  postalCode: z.string().trim(),
  city: z.string().max(255).trim(),
  state: z.string().trim().optional(),
});

export const bankDetailsBase = z.object({
  name: z.string().min(1).max(150).trim(),
  bicSwift: z.string().regex(/^[0-9A-Z]{8}$|^[0-9A-Z]{11}$/),
  accountType: z.enum(["checking", "savings"]),
  paymentType: z.enum(["priority", "regular"]),
  address: addressDetails,
});

export const bankDetailsIban = bankDetailsBase.extend({
  type: z.literal("iban"),
  iban: z.string().trim(),
});

export const bankDetailsAba = bankDetailsBase.extend({
  type: z.literal("aba"),
  accountNumber: z.string().trim(),
  aba: z.string().trim(),
});

export const bankDetails = z.discriminatedUnion("type", [bankDetailsIban, bankDetailsAba]);

export const partialBankDetailsModel = z.discriminatedUnion("type", [
  bankDetailsIban.deepPartial().extend(bankDetailsIban.pick({ type: true }).shape),
  bankDetailsAba.deepPartial().extend(bankDetailsAba.pick({ type: true }).shape),
]);

export const beneficiaryModel = z.object({
  id: z.string().uuid(),
  companyName: z.string().max(150).trim(),
  email: z.string().email().max(255).trim(),
  address: enhancedAddressDetails,
  bankDetails,
  currencyCode: z.string(),
  accountId: z.string().uuid(),
});

export const createBeneficiaryModel = beneficiaryModel
  .deepPartial()
  .extend({ bankDetails: partialBankDetailsModel });
export type CreateBeneficiaryModel = z.infer<typeof createBeneficiaryModel>;
