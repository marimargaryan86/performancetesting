import integrationInstances from "~/integration-instances";
import type * as HubSchemas from "~/integration/junction-hub-api/schemas";
import type { PaginatedData } from "$lib/models/common";
import { LIST_BILLS_LIMIT } from "./+page.svelte";
import { error } from "@sveltejs/kit";
import { permitted } from "$lib/utils/permissions";

export function load(event): { bills: Promise<PaginatedData<HubSchemas.Bill>> } {
  const user = event.locals.user;
  const session = event.locals.session;

  if (!user || !permitted(user, "*")) {
    throw error(401);
  }

  return {
    bills: integrationInstances.junctionHubApi.bills.find({
      session,
      limit: LIST_BILLS_LIMIT,
    }),
  };
}
