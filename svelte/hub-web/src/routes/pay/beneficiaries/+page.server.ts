import integrationInstances from "~/integration-instances";
import type * as HubSchemas from "~/integration/junction-hub-api/schemas";
import type { PaginatedData } from "$lib/models/common";
import { LIST_BENEFICIARIES_LIMIT } from "./+page.svelte";
import { dev } from "$app/environment";
import { error } from "@sveltejs/kit";

export async function load(event): Promise<{
  beneficiaries: PaginatedData<HubSchemas.Beneficiary>;
}> {
  if (!dev) {
    // TODO(2024-02-27): Remove once beneficiairies are enabled
    throw error(404);
  }

  return {
    beneficiaries: await integrationInstances.junctionHubApi.beneficiaries.find({
      session: event.locals.session,
      limit: LIST_BENEFICIARIES_LIMIT,
    }),
  };
}
