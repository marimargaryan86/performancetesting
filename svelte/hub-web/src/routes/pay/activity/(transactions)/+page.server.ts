import integrationInstances from "~/integration-instances";
import type * as HubSchemas from "~/integration/junction-hub-api/schemas";
import type { PaginatedData } from "$lib/models/common";
import { LIST_TRANSACTIONS_LIMIT, LIST_TRANSACTIONS_SORT } from "./+page.svelte";

export function load(event): {
  transactions: Promise<PaginatedData<HubSchemas.Transaction>>;
} {
  return {
    transactions: integrationInstances.junctionHubApi.transactions.find({
      session: event.locals.session,
      limit: LIST_TRANSACTIONS_LIMIT,
      sort: LIST_TRANSACTIONS_SORT,
    }),
  };
}
