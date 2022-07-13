import type { BalanceModel } from "./balance-models";

export type TransactionModel = {
  id: string;
  amount: number;
  ref: string;
  completedAt: Date;
  createdAt: Date;
  currencyCode: string;
  balance: BalanceModel;
  type: string;
  status: string;
};
