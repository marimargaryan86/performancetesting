import integrationInstances from "~/integration-instances";
import type * as HubSchemas from "~/integration/junction-hub-api/schemas";
import type { PaginatedData } from "$lib/models/common";
import { LIST_CONVERSIONS_LIMIT } from "./+page.svelte";

export async function load(event): Promise<{
  conversions: PaginatedData<HubSchemas.Conversion>;
}> {
  return {
    conversions: await integrationInstances.junctionHubApi.conversions.find({
      session: event.locals.session,
      limit: LIST_CONVERSIONS_LIMIT,
    }),
  };
}
