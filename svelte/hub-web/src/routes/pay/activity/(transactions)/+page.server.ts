import integrationInstances from "integration-instances";
import type { TransactionModel } from "models/transaction";
import { getToken } from "utils/auth";
import type { PageServerLoadEvent } from "./$types";

export async function load(
  event: PageServerLoadEvent,
): Promise<{ transactions: TransactionModel[]; transactionsCursor?: string }> {
  const [transactions, transactionsCursor] =
    await integrationInstances.junctionPay.transactions.listTransactions(getToken(event));

  return {
    transactions,
    transactionsCursor,
  };
}
