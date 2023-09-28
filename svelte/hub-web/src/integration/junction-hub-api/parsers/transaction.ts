import {
  transactionModel,
  type TransactionModel,
  type TransactionSchema,
} from "../schemas/transaction";
import type { CompanyModel } from "../schemas/company";

export function parseTransactionSchema(
  data: TransactionSchema,
  included: {
    companies?: CompanyModel[];
  } = {},
): TransactionModel {
  const beneficiary = included.companies?.find(
    (item) => item.id === data.relationships.beneficiary?.data.id,
  );
  const payer = included.companies?.find((item) => item.id === data.relationships.payer?.data.id);

  return {
    ...transactionModel.toModel(data),
    beneficiary,
    payer,
  };
}
