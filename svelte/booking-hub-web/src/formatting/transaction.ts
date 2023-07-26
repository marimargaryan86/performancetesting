import {
  balanceTransactionStatusMapping,
  transactionStatusMapping,
  type BalanceTransactionStatus,
  type TransactionStatus,
} from "models/transaction";

export function formatTransactionStatus(status: TransactionStatus): string {
  return transactionStatusMapping[status];
}

export function formatBalanceTransactionStatus(status: BalanceTransactionStatus): string {
  return balanceTransactionStatusMapping[status];
}
