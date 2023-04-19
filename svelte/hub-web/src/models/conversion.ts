import type { MoneyModel } from "./money";
import type { TransactionModel } from "./transaction";

export const conversionStatus = ["executed", "unspecified"] as const;

export type ConversionStatus = (typeof conversionStatus)[number];

export const conversionStatusMapping: Record<ConversionStatus, string> = {
  executed: "Executed",
  unspecified: "Unspecified",
};

export type ConversionModel = {
  id: string;
  executedAt: Date;
  settledAt: Date;
  sellAmount: MoneyModel;
  buyAmount: MoneyModel;
  executedRate: number;
  fxDelta: number | null;
  fxStatus: ConversionStatus;
  transaction?: TransactionModel;
};
