import integrationInstances from "~/integration-instances";
import type { Account } from "~/integration/junction-hub-api/schemas/account";
import type { PaginatedData } from "$lib/models/common";
import { LIST_ACCOUNTS_LIMIT } from "./+page.svelte";

export function load(event): { accounts: Promise<PaginatedData<Account>> } {
  return {
    accounts: integrationInstances.junctionHubApi.accounts.find({
      session: event.locals.session,
      limit: LIST_ACCOUNTS_LIMIT,
    }),
  };
}
