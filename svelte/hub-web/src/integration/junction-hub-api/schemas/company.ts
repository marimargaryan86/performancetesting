import type { Account } from "./account";
import * as CommonSchemas from "~/integration/common/schemas";
import type { IncludedMapping } from "./included";
import { moneyParser, type Money } from "./money";
import type { GetOKResponse } from "~/integration/common/types";
import type { Specification } from "./__generated__";

export type Company = {
  id: string;
  name: string;
  address?: CommonSchemas.EnhancedAddressDetails;
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

export type CompanySchema = NonNullable<
  GetOKResponse<Specification, "/companies/{companyId}">["data"]
>;

export const companyParser = {
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  toModel: (data: CompanySchema, included?: IncludedMapping): Company => {
    // TODO(2024-04-10): Figure out why this was removed from the spec
    // const accountId = data.relationships?.account?.data.id;

    return {
      id: data.id,
      name: data.attributes.name ?? "",
      address: data.attributes.address
        ? CommonSchemas.enhancedAddressDetailsParser.toModel(data.attributes.address)
        : undefined,
      markups: {
        fx: data.attributes.fxMarkup ?? 0,
        processing: data.attributes.processingMarkup ?? 0,
        sales: data.attributes.salesMarkup ?? 0,
        reseller: data.attributes.feeAmounts?.map(moneyParser.toModel) ?? [],
      },
      payment: {
        type: data.attributes.paymentType ?? "unspecified",
        method: data.attributes.paymentMethod ?? "unspecified",
      },
      // accountId,
      // account: included?.accounts?.find(({ id }) => id === accountId),
    };
  },
};
