import integrationInstances from "integration-instances";
import type { Journey } from "integration/junction-hub-api/schemas/journey";
import type { PaginatedData } from "models/common";
import { getSession } from "utils/auth";
import { LIST_JOURNEYS_LIMIT, LIST_JOURNEYS_SORT } from "./+page.svelte";

export function load(event): { journeys: Promise<PaginatedData<Journey>> } {
  return {
    journeys: integrationInstances.junctionHubApi.journeys.find({
      limit: LIST_JOURNEYS_LIMIT,
      session: getSession(event),
      sort: LIST_JOURNEYS_SORT,
    }),
  };
}
