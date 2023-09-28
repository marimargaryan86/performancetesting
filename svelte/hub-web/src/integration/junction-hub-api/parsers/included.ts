import {
  transactionModel,
  type TransactionModel,
  type TransactionSchema,
} from "../schemas/transaction";

type IncludeSchemas = {
  transactions: TransactionSchema[];
};

type IncludeModels = {
  transactions: TransactionModel[];
};

export function parseIncluded(data: TransactionSchema[]): IncludeModels {
  const mapping: IncludeSchemas = {
    transactions: data,
  };

  const transactions = mapping.transactions.map(transactionModel.toModel);

  return { transactions };
}
