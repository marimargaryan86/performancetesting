import type { CurrencyAmount } from "./currency";

export const transactionStatus = ["paid", "pending", "cancelled"] as const;

export const balanceTransactionStatus = ["completed", "pending", "deleted"] as const;

export type TransactionStatus = (typeof transactionStatus)[number];

export type BalanceTransactionStatus = (typeof balanceTransactionStatus)[number];

export const transactionStatusMapping: Record<TransactionStatus, string> = {
  cancelled: "Cancelled",
  paid: "Paid",
  pending: "Pending",
};

export const balanceTransactionStatusMapping: Record<BalanceTransactionStatus, string> = {
  deleted: "Deleted",
  completed: "Completed",
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

export interface BalanceTransactionModel {
  createdAt: Date;
  action: string;
  reason: string;
  debit: CurrencyAmount;
  credit: CurrencyAmount;
  balance: CurrencyAmount;
  status: BalanceTransactionStatus;
}
