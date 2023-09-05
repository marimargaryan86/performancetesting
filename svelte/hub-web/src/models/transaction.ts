import type { priceModel } from "integration/junction-mobile-api/schemas/price";
import type { CompanyModel } from "./company";
import type { Infer } from "integration/junction-mobile-api/schema-model.server";

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
    beneficiary: Infer<typeof priceModel>;
    quotation: Infer<typeof priceModel>;
    salesMargin: Infer<typeof priceModel>;
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
  debit: Infer<typeof priceModel>;
  credit: Infer<typeof priceModel>;
  balance: Infer<typeof priceModel>;
  status: BalanceTransactionStatus;
};
