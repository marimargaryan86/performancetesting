export type PriceBreakdownType =
  | "base-fare"
  | "tax"
  | "reseller-mark-up"
  | "company-mark-up"
  | "service-mark-up";

export interface PriceBreakdownSchema {
  price: PriceSchema;
  breakdownType: PriceBreakdownType;
}

export interface PriceSchema {
  currency: string;
  amount: string;
}
