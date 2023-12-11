import type { Account, AccountSchema } from "./account";
import {
  enhancedAddressDetailsParser,
  type EnhancedAddressDetails,
  type EnhancedAddressDetailsSchema,
} from "integration/common/schemas/address";
import type { IncludedMapping } from "./included";
import { moneyParser, type Money, type MoneySchema } from "./money";

export type Company = {
  id: string;
  name: string;
  address: EnhancedAddressDetails;
  markups: {
    fx: number;
    processing: number;
    sales: number;
    reseller: Money[];
  };
  payment: {
    type: "unspecified" | "card" | "bank-transfer";
    method: "unspecified" | "transactional" | "invoice";
  };
  accountId?: string;
  account?: Account;
};

export type CompanySchema = {
  id: string;
  type: "companies";
  attributes: {
    name: string;
    address: EnhancedAddressDetailsSchema;
    fxMarkup: number;
    processingMarkup: number;
    salesMarkup: number;
    feeAmounts: MoneySchema[];
    feeMultiplier: number;
    paymentType: "unspecified" | "card" | "bank-transfer";
    paymentMethod: "unspecified" | "transactional" | "invoice";
  };
  relationships?: {
    account?: { data: Pick<AccountSchema, "id" | "type"> };
  };
};

export const companyParser = {
  toModel: (data: CompanySchema, included?: IncludedMapping): Company => {
    const accountId = data.relationships?.account?.data.id;
    return {
      id: data.id,
      name: data.attributes.name,
      address: enhancedAddressDetailsParser.toModel(data.attributes.address),
      markups: {
        fx: data.attributes.fxMarkup,
        processing: data.attributes.processingMarkup,
        sales: data.attributes.salesMarkup,
        reseller: data.attributes.feeAmounts.map(moneyParser.toModel),
      },
      payment: {
        type: data.attributes.paymentType,
        method: data.attributes.paymentMethod,
      },
      accountId,
      account: included?.accounts?.find(({ id }) => id === accountId),
    };
  },
};
