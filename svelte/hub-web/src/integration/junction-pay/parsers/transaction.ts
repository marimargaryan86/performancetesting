import type { CompanyModel } from "models/company";
import {
  transactionStatus,
  type TransactionModel,
  type TransactionStatus,
} from "models/transaction";
import type { TransactionSchema } from "../schemas/transaction";

export function parseTransactionSchema(
  transaction: TransactionSchema,
  companies: CompanyModel[] = [],
): TransactionModel {
  const { attributes, relationships } = transaction;
  const beneficiary = companies.find((item) => item.id === relationships.beneficiary.data.id);
  const payer = companies.find((item) => item.id === relationships.payer.data.id);

  return {
    id: transaction.id,
    bookingId: attributes.externalReference,
    beneficiary,
    createdAt: new Date(attributes.createdAt),
    payer,
    amounts: {
      beneficiary: attributes.amounts.beneficiary,
      quotation: attributes.amounts.quotation,
      salesMargin: attributes.amounts.salesMargin,
    },
    rates: {
      fxBuffer: attributes.rates.fxBuffer,
      fxMarkup: attributes.rates.fxMarkup,
      fxQuote: attributes.rates.fxQuote,
      salesMarkup: attributes.rates.salesMarkup,
    },
    reference: attributes.invoiceReference,
    // eslint-disable-next-line no-warning-comments
    // TODO: Use real status.
    status: transactionStatus[0] as TransactionStatus,
  };
}
