import type { CompanyModel } from "models/company";
import {
  transactionStatus,
  type TransactionModel,
  type TransactionStatus,
} from "models/transaction";
import type { TransactionSchema } from "../schemas/transaction";

export function parseTransaction(
  transaction: TransactionSchema,
  companies: CompanyModel[],
): TransactionModel {
  const { attributes, relationships } = transaction;
  const beneficiary = companies.find((item) => item.id === relationships.beneficiary.data.id);
  const payer = companies.find((item) => item.id === relationships.payer.data.id);

  if (!beneficiary) {
    throw new Error("Error parsing transaction: Beneficiary not found");
  }

  if (!payer) {
    throw new Error("Error parsing transaction: Payer not found");
  }

  return {
    id: transaction.id,
    beneficiary,
    createdAt: new Date(attributes.createdAt),
    parentId: attributes.parentExternalReference,
    payer,
    amounts: {
      beneficiary: attributes.amounts.beneficiary,
      quotation: attributes.amounts.quotation,
      salesMargin: attributes.amounts.salesMargin,
    },
    reference: attributes.externalReference,
    /* eslint-disable no-warning-comments */
    // TODO: Use real status.
    status: transactionStatus[Math.floor(Math.random() * 3)] as TransactionStatus,
  };
}
