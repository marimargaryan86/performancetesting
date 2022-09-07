import type { BalanceIdentifier } from "./balance-schemas";
import type { Identifier } from "./base-schemas";
import type { CurrencyIdentifier } from "./currency-schemas";

export type TransactionTypeIdentifier = Identifier & {
  type: "transaction-types";
};

export type TransactionStatusIdentifier = Identifier & {
  type: "transaction-statuses";
};

export type TransactionsResponse = {
  data: (Identifier & {
    attributes: {
      amount: number;
      ref: string;
      completedAt: string;
      createdAt: string;
    };
    relationships: {
      balance: {
        data: BalanceIdentifier;
      };
      currency: {
        data: CurrencyIdentifier;
      };
      transactionType: {
        data: TransactionTypeIdentifier;
      };
      status: {
        data: TransactionStatusIdentifier;
      };
    };
  })[];
  links: {
    next: string;
  };
};
