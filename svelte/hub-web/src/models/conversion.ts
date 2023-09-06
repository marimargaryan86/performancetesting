import type { PriceModel } from "integration/junction-mobile-api/schemas/price";
import type { TransactionModel } from "./transaction";

export const conversionStatus = ["executed", "unspecified", "failed"] as const;

export type ConversionStatus = (typeof conversionStatus)[number];

export const conversionStatusMapping: Record<ConversionStatus, string> = {
  executed: "Executed",
  unspecified: "Unspecified",
  failed: "Failed",
};

export type ConversionModel = {
  id: string;
  createdAt?: Date;
  settledAt?: Date;
  sellAmount?: PriceModel;
  buyAmount: PriceModel;
  executedRate: number;
  fxDelta?: number;
  fxStatus: ConversionStatus;
  transaction?: TransactionModel;
};
