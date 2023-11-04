import type { Merge, Partialize, Require } from "integration/ts-helpers";
import type { Account, AccountSchema } from "./account";
import {
  enhancedAddressDetailsParser,
  type EnhancedAddressDetails,
  type EnhancedAddressDetailsSchema,
} from "./address";
import type { IncludedMapping } from "./included";
import { moneyParser, type Money, type MoneySchema } from "./money";

export type Company = {
  id: string;
  name?: string;
  address?: EnhancedAddressDetails;
  markups: {
    fx?: number;
    processing?: number;
    sales?: number;
    reseller?: Money[];
  };
  payment: {
    type?: "unspecified" | "card" | "bank-transfer";
    method?: "unspecified" | "transactional" | "invoice";
  };
  accountId?: string;
  account?: Account;
};

export type CompanyCreate = Merge<
  Require<Omit<Company, "id">, "name" | "address">,
  {
    markups: Partialize<Required<Company["markups"]>, "reseller">;
    payment: Required<Company["payment"]>;
  }
>;

export type CompanyUpdate = Omit<Company, "id">;

export type CompanySchema = {
  id: string;
  type: "companies";
  attributes: {
    name?: string;
    address?: EnhancedAddressDetailsSchema;
    fxMarkup?: number;
    processingMarkup?: number;
    salesMarkup?: number;
    resellerMarkups?: MoneySchema[];
    paymentType?: "unspecified" | "card" | "bank-transfer";
    paymentMethod?: "unspecified" | "transactional" | "invoice";
  };
  relationships?: {
    account?: { data: Pick<AccountSchema, "id" | "type"> };
  };
};

export type CompanyCreateSchema = Pick<CompanySchema, "type"> & {
  attributes: Partialize<Required<CompanySchema["attributes"]>, "resellerMarkups">;
};

export type CompanyUpdateSchema = Omit<CompanySchema, "id" | "relationships">;

export const companyParser = {
  toModel: (data: CompanySchema, included?: IncludedMapping): Company => {
    const accountId = data.relationships?.account?.data.id;
    return {
      id: data.id,
      name: data.attributes.name,
      address: data.attributes.address
        ? enhancedAddressDetailsParser.toModel(data.attributes.address)
        : undefined,
      markups: {
        fx: data.attributes.fxMarkup,
        processing: data.attributes.processingMarkup,
        sales: data.attributes.salesMarkup,
        reseller: data.attributes.resellerMarkups?.map(moneyParser.toModel),
      },
      payment: {
        type: data.attributes.paymentType,
        method: data.attributes.paymentMethod,
      },
      accountId,
      account: included?.accounts?.find(({ id }) => id === accountId),
    };
  },
  toCreateSchema: (data: CompanyCreate): CompanyCreateSchema => ({
    type: "companies",
    attributes: {
      name: data.name,
      address: enhancedAddressDetailsParser.toSchema(data.address),
      fxMarkup: data.markups.fx,
      processingMarkup: data.markups.processing,
      salesMarkup: data.markups.sales,
      resellerMarkups: data.markups.reseller?.map(moneyParser.toSchema),
      paymentMethod: data.payment.method,
      paymentType: data.payment.type,
    },
  }),
  toUpdateSchema: (data: CompanyUpdate): CompanyUpdateSchema => ({
    type: "companies",
    attributes: {
      name: data.name,
      address: data.address ? enhancedAddressDetailsParser.toSchema(data.address) : undefined,
      fxMarkup: data.markups.fx,
      processingMarkup: data.markups.processing,
      salesMarkup: data.markups.sales,
      resellerMarkups: data.markups.reseller?.map(moneyParser.toSchema),
      paymentMethod: data.payment.method,
      paymentType: data.payment.type,
    },
  }),
};
