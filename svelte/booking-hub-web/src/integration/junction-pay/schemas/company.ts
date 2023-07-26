import type { AddressDetailsSchema } from "./contact";

export interface CompanyIdentifierSchema {
  id: string;
  type: "companies";
}

export interface CompanyDetailsSchema extends CompanyIdentifierSchema {
  attributes: {
    name: string;
    address: AddressDetailsSchema;
    bufferRate: number;
    salesRate: number;
  };
}

export interface GetCompanyDetailsResponseSchema {
  data: CompanyDetailsSchema;
}
