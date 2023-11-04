import type { IncludedMapping } from "./included";
import { moneyParser, type Money, type MoneySchema } from "./money";
import type { Transaction, TransactionSchema } from "./transaction";

export type Conversion = {
  id: string;
  createdAt?: Date;
  settledAt?: Date;
  amounts: {
    buy?: Money;
    sell?: Money;
  };
  executedRate?: number;
  fx: {
    delta?: number;
    status?: "unspecified" | "executed" | "failed";
  };
  transactionId?: string;
  transaction?: Transaction;
};

export type ConversionSchema = {
  id: string;
  type: "conversions";
  attributes: {
    createdAt?: string;
    settledAt?: string;
    sellAmount?: MoneySchema;
    buyAmount?: MoneySchema;
    executedRate?: number;
    fxDelta?: number | null;
    fxStatus?: "unspecified" | "executed" | "failed";
  };
  relationships?: {
    transactions: { data: Pick<TransactionSchema, "id" | "type"> };
  };
  links: { self: string };
};

export const conversionParser = {
  toModel: (data: ConversionSchema, included?: IncludedMapping): Conversion => {
    const transactionId = data.relationships?.transactions.data.id;

    return {
      id: data.id,
      createdAt: data.attributes.createdAt ? new Date(data.attributes.createdAt) : undefined,
      settledAt: data.attributes.settledAt ? new Date(data.attributes.settledAt) : undefined,
      amounts: {
        buy: data.attributes.buyAmount ? moneyParser.toModel(data.attributes.buyAmount) : undefined,
        sell: data.attributes.sellAmount
          ? moneyParser.toModel(data.attributes.sellAmount)
          : undefined,
      },
      fx: {
        delta: data.attributes.fxDelta ?? undefined,
        status: data.attributes.fxStatus,
      },
      executedRate: data.attributes.executedRate,
      transactionId,
      transaction: included?.transactions?.find(({ id }) => id === transactionId),
    };
  },
};
