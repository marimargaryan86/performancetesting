import integrationInstances from "~/integration-instances";
import type * as HubSchemas from "~/integration/junction-hub-api/schemas";
import type { PaginatedData } from "$lib/models/common";
import { LIST_RESELLERS_LIMIT } from "./+page.svelte";

export async function load(event): Promise<{ resellers: PaginatedData<HubSchemas.Reseller> }> {
  return {
    resellers: await integrationInstances.junctionHubApi.resellers.find({
      limit: LIST_RESELLERS_LIMIT,
      session: event.locals.session,
    }),
  };
}
