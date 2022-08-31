import type {
  BankAccountType,
  EntityType,
  IdentificationType,
  PaymentType,
} from "../../schemas/beneficiaries";
import type { RecursivePartial } from "../common";

export type BeneficiaryRequiredModel = {
  bank: {
    account: {
      holderName: string;
      currencyCode: string;
    };
    countryCode: string;
  };
  nickname: string;
};

export type BeneficiaryOptionalBaseModel<T = EntityType | null> = {
  default: boolean;
  entityType: T;
  bank: {
    account: {
      number: string | null;
      sortCode: string | null;
      bic: string | null;
      iban: string | null;
      type: BankAccountType | null;
    };
    name: string | null;
  };
  contact: {
    email: string | null;
    postalCode: string | null;
    city: string | null;
    countryCode: string | null;
    stateOrProvince: string | null;
    externalReference: string | null;
  };
  identification: {
    type: IdentificationType | null;
    value: string | null;
  };
};

export type BeneficiaryOptionalModel<T = EntityType | null> = T extends "company"
  ? BeneficiaryOptionalBaseModel<T> & {
      company: {
        name: string | null;
        registrationDate: Date | null;
      };
    }
  : T extends "individual"
  ? BeneficiaryOptionalBaseModel<T> & {
      individual: {
        firstName: string | null;
        lastName: string | null;
        birthDate: Date | null;
      };
    }
  : BeneficiaryOptionalBaseModel<T>;

export type BeneficiaryPutModel<T = EntityType | null> = BeneficiaryRequiredModel &
  RecursivePartial<
    BeneficiaryOptionalModel<T> & {
      onBehalfOf: string | null;
      paymentTypes: PaymentType[];
      bank: {
        address: string | null;
      };
      contact: {
        address: string | null;
      };
    }
  >;

export type BeneficiaryModel<T = EntityType | null> = BeneficiaryRequiredModel &
  BeneficiaryOptionalModel<T> & {
    id: string;
    paymentTypes: PaymentType[];
    createdAt: Date;
    modifiedAt: Date;
    creatorId: string;
    bank: {
      address: string[];
    };
    contact: {
      address: string[];
    };
  };
