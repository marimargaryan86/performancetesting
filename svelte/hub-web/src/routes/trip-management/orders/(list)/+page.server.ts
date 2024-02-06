import integrationInstances from "~/integration-instances";
import type { Journey } from "~/integration/junction-hub-api/schemas/journey";
import type { PaginatedData } from "~/models/common";
import { LIST_JOURNEYS_LIMIT, LIST_JOURNEYS_SORT, queryFiltersGetter } from "./+page.svelte";

export function load(event): { journeys: Promise<PaginatedData<Journey>> } {
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
