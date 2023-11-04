import integrationInstances from "integration-instances";
import type { Conversion } from "integration/junction-hub-api/schemas/conversion";
import type { PaginatedData } from "models/common";
import { getSession } from "utils/auth";
import { LIST_CONVERSIONS_LIMIT } from "./+page.svelte";

export function load(event): {
  conversions: Promise<PaginatedData<Conversion>>;
} {
  return {
    conversions: integrationInstances.junctionHubApi.conversions.find({
      session: getSession(event),
      limit: LIST_CONVERSIONS_LIMIT,
    }),
  };
}
