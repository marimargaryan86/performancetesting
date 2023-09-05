import type { priceModel } from "integration/junction-mobile-api/schemas/price";
import type { TransactionModel } from "./transaction";
import type { Infer } from "integration/junction-mobile-api/schema-model.server";

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
  sellAmount?: Infer<typeof priceModel>;
  buyAmount: Infer<typeof priceModel>;
  executedRate: number;
  fxDelta?: number;
  fxStatus: ConversionStatus;
  transaction?: TransactionModel;
};
