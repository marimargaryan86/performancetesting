import integrationInstances from "~/integration-instances";
import type * as HubSchemas from "~/integration/junction-hub-api/schemas";
import type { PaginatedData } from "$lib/models/common";
import { LIST_BENEFICIARIES_LIMIT } from "./+page.svelte";

export function load(event): {
  beneficiaries: Promise<PaginatedData<HubSchemas.Beneficiary>>;
} {
  return {
    beneficiaries: integrationInstances.junctionHubApi.beneficiaries.find({
      session: event.locals.session,
      limit: LIST_BENEFICIARIES_LIMIT,
    }),
  };
}
