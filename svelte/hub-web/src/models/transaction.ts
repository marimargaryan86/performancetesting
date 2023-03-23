import type { CompanyModel } from "./company";
import type { MoneyModel } from "./money";

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
  payer: CompanyModel;
  offerAmount: MoneyModel;
  beneficiary: CompanyModel;
  beneficiaryAmount: MoneyModel;
  profit: MoneyModel;
  reference: string;
  status: TransactionStatus;
}

export interface BalanceTransactionModel {
  createdAt: Date;
  action: string;
  reason: string;
  debit: MoneyModel;
  credit: MoneyModel;
  balance: MoneyModel;
  status: BalanceTransactionStatus;
}
