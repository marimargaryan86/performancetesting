import type { AccountIdentifierSchema } from "./account";
import type { RelationshipSchema } from "./common";
import type { CurrencyIdentifierSchema } from "./money";

export const paymentTypes = ["priority", "regular"] as const;

export type PaymentType = (typeof paymentTypes)[number];

export const accountTypes = ["checking", "savings"] as const;

export type AccountType = (typeof accountTypes)[number];

export interface AddressDetails {
  addressLines: string[];
  countryCode: string;
}

export interface EnhancedAddressDetails extends AddressDetails {
  postalCode?: string;
  city?: string;
  state?: string | null;
}

export interface BaseBankDetailsSchema {
  name: string;
  bicSwift?: string | null;
  accountType: AccountType;
  paymentTypes: PaymentType;
  address: AddressDetails;
}

export interface BankDetailsAbaSchema extends BaseBankDetailsSchema {
  accountNumber: string | null;
  aba: string | null;
}

export interface BankDetailsIbanSchema extends BaseBankDetailsSchema {
  iban: string | null;
}

export type BankDetailsSchema = BankDetailsAbaSchema | BankDetailsIbanSchema;

export interface BeneficiaryIdentifierSchema {
  id: string;
  type: "beneficiaries";
}

export interface BeneficiarySchema extends BeneficiaryIdentifierSchema {
  attributes: {
    bankAccountHolderName: string;
    email: string;
    beneficiaryAddress: EnhancedAddressDetails;
    bankDetails: BankDetailsSchema;
  };
  relationships: {
    currency: RelationshipSchema<CurrencyIdentifierSchema>;
    account: RelationshipSchema<AccountIdentifierSchema>;
  };
  links: { self: string };
}

export interface CreateBeneficiaryRequestSchema {
  data: Omit<BeneficiarySchema, "id">;
}

export interface CreateBeneficiaryResponseSchema {
  data: BeneficiarySchema;
}

export interface ListBeneficiariesResponseSchema {
  data: BeneficiarySchema[];
  links: { next: string };
}

export interface GetBeneficiaryResponseSchema {
  data: BeneficiarySchema;
}
