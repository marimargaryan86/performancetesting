import type { PriceBreakdownType } from "integration/junction-client-api/schemas/price";

export interface PriceModel {
  currency: string;
  amount: number;
}

export interface PriceBreakdownModel {
  price: PriceModel;
  type: PriceBreakdownType;
}
