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

export type TransactionModel = {
  id: string;
  bookingId: string;
  createdAt: Date;
  payer?: CompanyModel;
  amounts: {
    beneficiary: MoneyModel;
    quotation: MoneyModel;
    salesMargin: MoneyModel;
  };
  rates: {
    fxQuote: number;
    fxBuffer: number;
    salesMarkup: number;
    fxMarkup: number;
  };
  beneficiary?: CompanyModel;
  reference: string;
  status: TransactionStatus;
};

export type BalanceTransactionModel = {
  createdAt: Date;
  action: string;
  reason: string;
  debit: MoneyModel;
  credit: MoneyModel;
  balance: MoneyModel;
  status: BalanceTransactionStatus;
};
