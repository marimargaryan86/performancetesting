import integrationInstances from "integration-instances";
import type { Beneficiary } from "integration/junction-hub-api/schemas/beneficiary";
import type { PaginatedData } from "models/common";
import { getSession } from "utils/auth";
import { LIST_BENEFICIARIES_LIMIT } from "./+page.svelte";

export function load(event): {
  beneficiaries: Promise<PaginatedData<Beneficiary>>;
} {
  return {
    beneficiaries: integrationInstances.junctionHubApi.beneficiaries.find({
      session: getSession(event),
      limit: LIST_BENEFICIARIES_LIMIT,
    }),
  };
}
