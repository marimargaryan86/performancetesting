import type { ConversionStatus } from "integration/junction-pay/schemas/conversion";
import type { MoneyModel } from "./money";
import type { TransactionModel } from "./transaction";

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
