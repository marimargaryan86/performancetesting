import type { GetOKResponse } from "~/integration/common/types";
import type { Specification } from "./__generated__";

export type Currency = {
  code: string;
  name: string;
  minorUnits: number;
};

export type CurrencySchema = GetOKResponse<Specification, "/currencies/{currencyName}">["data"];

export const currencyParser = {
  toModel: (data: CurrencySchema): Currency => ({
    code: data.id,
    name: data.attributes.name,
    minorUnits: data.attributes.minorUnits,
  }),
};
