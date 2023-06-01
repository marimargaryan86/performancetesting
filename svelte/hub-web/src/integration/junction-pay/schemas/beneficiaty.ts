import type { AccountIdentifierSchema } from "./account";
import type { RelationshipSchema } from "./common";
import type { CurrencyIdentifierSchema } from "./money";

export interface AddressDetails {
  addressLines: string[];
  countryCode: string;
}

export interface EnhancedAddressDetails extends AddressDetails {
  postalCode?: string;
  city?: string;
  state?: string | null;
}

export interface BaseBankDetails {
  name: string;
  bicSwift?: string | null;
  accountType: "checking" | "savings";
  paymentTypes: "priority" | "regular";
  address: AddressDetails;
}

export interface BankDetailsAba extends BaseBankDetails {
  accountNumber: string | null;
  aba: string | null;
}

export interface BankDetailsIban extends BaseBankDetails {
  iban: string | null;
}

export interface BeneficiaryIdentifierSchema {
  id: string;
  type: "beneficiaries";
}

export interface BeneficiarySchema extends BeneficiaryIdentifierSchema {
  attributes: {
    bankAccountHolderName: string;
    email: string;
    beneficiaryAddress: EnhancedAddressDetails;
    bankDetails: BankDetailsAba | BankDetailsIban;
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
