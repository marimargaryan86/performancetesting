import integrationInstances from "~/integration-instances";
import type { Conversion } from "~/integration/junction-hub-api/schemas/conversion";
import type { PaginatedData } from "$lib/models/common";
import { LIST_CONVERSIONS_LIMIT } from "./+page.svelte";

export function load(event): {
  conversions: Promise<PaginatedData<Conversion>>;
} {
  return {
    conversions: integrationInstances.junctionHubApi.conversions.find({
      session: event.locals.session,
      limit: LIST_CONVERSIONS_LIMIT,
    }),
  };
}
