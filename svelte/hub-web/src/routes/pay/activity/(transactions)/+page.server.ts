import integrationInstances from "integration-instances";
import type { Transaction } from "integration/junction-hub-api/schemas/transaction";
import type { PaginatedData } from "models/common";
import { getSession } from "utils/auth";
import { LIST_TRANSACTIONS_LIMIT } from "./+page.svelte";

export function load(event): {
  transactions: Promise<PaginatedData<Transaction>>;
} {
  return {
    transactions: integrationInstances.junctionHubApi.transactions.find({
      session: getSession(event),
      limit: LIST_TRANSACTIONS_LIMIT,
    }),
  };
}
