import integrationInstances from "~/integration-instances";
import type * as HubSchemas from "~/integration/junction-hub-api/schemas";
import type { PaginatedData } from "$lib/models/common";
import { LIST_JOURNEYS_LIMIT, LIST_JOURNEYS_SORT } from "./+page.svelte";
import { queryFiltersGetter } from "$lib/components/pages/trip-management/orders/filters.svelte";

export function load(event): { journeys: Promise<PaginatedData<HubSchemas.Journey>> } {
  const filter = queryFiltersGetter(Object.fromEntries(event.url.searchParams));

  return {
    journeys: integrationInstances.junctionHubApi.journeys.find({
      limit: LIST_JOURNEYS_LIMIT,
      session: event.locals.session,
      sort: LIST_JOURNEYS_SORT,
      filter,
    }),
  };
}
