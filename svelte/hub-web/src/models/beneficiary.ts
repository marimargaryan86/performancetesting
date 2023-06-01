import type { CurrencyModel } from "./money";

export type BeneficiaryModel = {
  id: string;
  name: string;
  currency: CurrencyModel;
  countryName: string;
  type: "priority" | "regular";
};
