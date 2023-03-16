import { transactionStatusMapping, type TransactionStatus } from "models/transaction";

export function formatTransactionStatus(status: TransactionStatus): string {
  return transactionStatusMapping[status];
}
