import type {
  BankAccountType,
  EntityType,
  IdentificationType,
  PaymentType,
  ScopeType,
} from "$integration/currency-cloud/schemas/beneficiaries";
import type { RecursivePartial } from "$models/common-models";
import type { OrderField } from "$integration/currency-cloud/models/beneficiaries/find";

export type CreateBeneficiaryBaseSchema = {
  nickname: string;
  bank: {
    account: {
      holderName: string;
      currencyCode: string;
      number?: string | null;
      bic?: string | null;
      iban?: string | null;
      type?: BankAccountType | null;
      sortCode?: string | null;
    };
    countryCode: string;
    address?: string | null;
    name?: string | null;
  };
  default?: boolean;
  entityType?: EntityType | null;
  contact?: {
    email?: string | null;
    address?: string | null;
    postalCode?: string | null;
    city?: string | null;
    stateOrProvince?: string | null;
    countryCode?: string | null;
    externalReference?: string | null;
  };
  identification?: {
    type: IdentificationType | null;
    value: string | null;
  };
  paymentTypes?: PaymentType[];
};

export type CreateCompanyBeneficiarySchema = CreateBeneficiaryBaseSchema & {
  entityType: "company";
  company?: {
    name: string;
    registrationDate: string;
  };
};

export type CreateIndividualBeneficiarySchema = CreateBeneficiaryBaseSchema & {
  entityType: "individual";
  individual?: {
    firstName: string;
    lastName: string;
    birthDate: string;
  };
};

export type CreateUnknownBeneficiarySchema = CreateBeneficiaryBaseSchema & {
  entityType?: undefined;
};

export type CreateBeneficiarySchema =
  | CreateUnknownBeneficiarySchema
  | CreateCompanyBeneficiarySchema
  | CreateIndividualBeneficiarySchema;

export type GetRequirementsSchema = {
  bankAccountCurrencyCode: string;
  bankAccountCountryCode: string;
  contactCountryCode?: string;
  entityType?: EntityType;
  paymentTypes?: PaymentType[];
};

export type FindCriteriaSchema = {
  bankAccountHolderName?: string;
  bankAccountCurrencyCode?: string;
  bankAccountNumber?: string;
  bankAccountSortCode?: string;
  bankAccountBic?: string;
  bankAccountIban?: string;
  defaultBeneficiary?: boolean;
  bankName?: string;
  bankAccountType?: BankAccountType;
  nickname?: string;
  entityType?: EntityType;
  companyName?: string;
  companyRegistrationDate?: string;
  individualFirstName?: string;
  individualLastName?: string;
  individualBirthDate?: string;
  contactCountryCode?: string;
  contactCity?: string;
  contactPostalCode?: string;
  contactStateOrProvince?: string;
  contactExternalReference?: string;
  scope?: ScopeType;
  "page[offset]"?: number;
  "page[limit]"?: number;
  "orderBy[asc]"?: OrderField;
  "orderBy[desc]"?: OrderField;
};

export type UpdateBeneficiarySchema = RecursivePartial<CreateBeneficiarySchema>;

export type BeneficiaryPutSchema = {
  // TODO: Impl.
};
