import type { CurrencyAmount } from "./currency";

export const transactionStatus = ["paid", "pending", "cancelled"] as const;

export type TransactionStatus = (typeof transactionStatus)[number];

export const transactionStatusMapping: Record<TransactionStatus, string> = {
  cancelled: "Cancelled",
  paid: "Paid",
  pending: "Pending",
};

export interface TransactionModel {
  id: string;
  parentId: string;
  createdAt: Date;
  payer: string;
  theyOwe: CurrencyAmount;
  beneficiery: string;
  weOwe: CurrencyAmount;
  profit: CurrencyAmount;
  reference: string;
  status: TransactionStatus;
}
