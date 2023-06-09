import { accountTypes, paymentTypes } from "integration/junction-pay/schemas/beneficiaty";
import { z } from "zod";

export const addressDetails = z.object({
  addressLines: z.array(z.string().min(1).max(255).trim()).min(1),
  countryCode: z.string().regex(/^[A-Z]{2}$/),
});

export const enhancedAddressDetailsModel = addressDetails.extend({
  postalCode: z.string().min(1).trim().optional(),
  city: z.string().min(1).max(255).min(1).trim().optional(),
  state: z.string().min(1).trim().optional(),
});

export const bankDetailsBaseModel = z.object({
  name: z.string().min(1).max(150).trim(),
  bicSwift: z.string().regex(/^[0-9A-Z]{8}$|^[0-9A-Z]{11}$/),
  accountType: accountTypes,
  paymentType: paymentTypes,
  address: addressDetails,
});

export const bankDetailsIbanModel = bankDetailsBaseModel.extend({
  type: z.enum(["iban"]),
  iban: z.string().min(1).trim(),
});

export const bankDetailsAbaModel = bankDetailsBaseModel.extend({
  type: z.enum(["aba"]),
  accountNumber: z.string().min(1).trim(),
  aba: z.string().min(1).trim(),
});

export const bankDetailsModel = z.discriminatedUnion("type", [
  bankDetailsIbanModel,
  bankDetailsAbaModel,
]);

export const partialBankDetailsModel = z.discriminatedUnion("type", [
  bankDetailsIbanModel.deepPartial().extend({ type: bankDetailsIbanModel._def.shape().type }),
  bankDetailsAbaModel.deepPartial().extend({ type: bankDetailsAbaModel._def.shape().type }),
]);

export const beneficiaryModel = z.object({
  id: z.string().uuid(),
  companyName: z.string().min(1).max(150).trim(),
  email: z.string().email().max(255).trim(),
  address: enhancedAddressDetailsModel,
  bankDetails: bankDetailsModel,
  currencyCode: z.string().regex(/^[A-Z]{3}$/),
  accountId: z.string().uuid(),
});

export const createBeneficiaryModel = beneficiaryModel
  .deepPartial()
  .extend({ bankDetails: partialBankDetailsModel });

export type AddressDetails = z.infer<typeof addressDetails>;

export type EnhancedAddressDetailsModel = z.infer<typeof enhancedAddressDetailsModel>;

export type BankDetailsBaseModel = z.infer<typeof bankDetailsBaseModel>;

export type BankDetailsIbanModel = z.infer<typeof bankDetailsIbanModel>;

export type BankDetailsAbaModel = z.infer<typeof bankDetailsAbaModel>;

export type BankDetailsModel = z.infer<typeof bankDetailsModel>;

export type BeneficiaryModel = z.infer<typeof beneficiaryModel>;

export type CreateBeneficiaryModel = z.infer<typeof createBeneficiaryModel>;
