import {
  conversionModel,
  type ConversionModel,
  type ConversionSchema,
} from "../schemas/conversion";
import type { TransactionModel } from "../schemas/transaction";

export function parseConversionSchema(
  data: ConversionSchema,
  included: {
    transactions?: TransactionModel[];
  } = {},
): ConversionModel {
  const transaction = included.transactions?.find(
    (item) => item.id === data.relationships?.transactions.data.id,
  );

  return { ...conversionModel.toModel(data), transaction };
}
