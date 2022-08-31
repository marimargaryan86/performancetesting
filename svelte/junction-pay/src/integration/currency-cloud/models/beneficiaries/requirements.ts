import type { EntityType, PaymentType } from "../../schemas/beneficiaries";

export type GetRequirementsModel = {
  entityType?: EntityType;
  paymentTypes?: PaymentType[];
  bank: {
    account: {
      countryCode: string;
      currencyCode: string;
    };
  };
  contact?: {
    countryCode?: string;
  };
};

export type RequirementsBaseModel<T = EntityType> = {
  paymentType: PaymentType;
  entityType: T;
  bank: {
    account: {
      number: boolean;
      sortCode: boolean;
      iban: boolean;
      bic: boolean;
    };
  };
  contact: {
    address: boolean;
    postalCode: boolean;
    city: boolean;
    stateOrProvince: boolean;
    countryCode: boolean;
  };
};

export type RequirementsModel<T = EntityType> = T extends "company"
  ? RequirementsBaseModel<T> & {
      company: {
        name: boolean;
        registrationDate: boolean;
      };
    }
  : T extends "individual"
  ? RequirementsBaseModel<T> & {
      individual: {
        firstName: boolean;
        lastName: boolean;
        birthDate: boolean;
      };
    }
  : never;
