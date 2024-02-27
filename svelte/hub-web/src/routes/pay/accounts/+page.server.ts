import integrationInstances from "~/integration-instances";
import type * as HubSchemas from "~/integration/junction-hub-api/schemas";
import type { PaginatedData } from "$lib/models/common";
import { LIST_ACCOUNTS_LIMIT } from "./+page.svelte";
import { dev } from "$app/environment";
import { error } from "@sveltejs/kit";

export function load(event): { accounts: Promise<PaginatedData<HubSchemas.Account>> } {
  if (!dev) {
    // TODO(2024-02-27): Remove once accounts are enabled
    throw error(404);
  }

  return {
    accounts: integrationInstances.junctionHubApi.accounts.find({
      session: event.locals.session,
      limit: LIST_ACCOUNTS_LIMIT,
    }),
  };
}
