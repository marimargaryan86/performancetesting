import integrationInstances from "~/integration-instances";
import type * as HubSchemas from "~/integration/junction-hub-api/schemas";
import type { PaginatedData } from "$lib/models/common";
import { LIST_BILLS_LIMIT } from "./+page.svelte";
import { error } from "@sveltejs/kit";
import { permitted } from "$lib/utils/permissions";

export async function load(event): Promise<{ bills: PaginatedData<HubSchemas.Bill> }> {
  const user = event.locals.user;
  const session = event.locals.session;

  if (!user || !permitted(user, "*")) {
    throw error(401);
  }

  return {
    bills: await integrationInstances.junctionHubApi.bills.find({
      session,
      limit: LIST_BILLS_LIMIT,
    }),
  };
}
