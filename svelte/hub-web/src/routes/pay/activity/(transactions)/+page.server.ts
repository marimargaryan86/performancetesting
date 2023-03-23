import integrationInstances from "integration-instances";
import type { TransactionModel } from "models/transaction";
import { getToken } from "utils/auth";
import type { PageServerLoadEvent } from "./$types";

export async function load(
  event: PageServerLoadEvent,
): Promise<{ transactions: TransactionModel[] }> {
  const token = getToken(event);

  return {
    transactions: await integrationInstances.junctionPay.transactions.listTransactions(token),
  };
}
